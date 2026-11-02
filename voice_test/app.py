from flask import Flask, render_template, request, jsonify, redirect, url_for
from threading import Thread

from farm_simulation import farm_state
from dashboard_state import dashboard_state

from task_queue import (
    add_task,
    get_tasks,
    get_task_count,
    verify_queued_tasks
)

from web_controller import (
    record_voice,
    process_recorded_command,
    process_selected_command,
    check_contract
)

from task_executor import execute_task
from execution_monitor import monitor_execution
from execution_recovery import recover_from_violation


from resource_database import (
    initialize_database,
    get_resources,
    add_resource,
    get_resource_history,
    set_resource_quantity
)


def initialize_resource_state():
    """Load saved resource quantities into the farm state."""
    initialize_database()

    saved_resources = get_resources()

    for name, details in saved_resources.items():
        farm_state["resources"][name] = details["quantity"]


initialize_resource_state()


app = Flask(__name__)

app.secret_key = "smart-agriculture-demo-secret-key"

def add_workflow_activity(message):
    """Store workflow events for the dashboard."""
    dashboard_state.setdefault("workflow_activity", [])
    dashboard_state["workflow_activity"].append(message)

# ============================================================
# VOICE RECOGNITION WORKFLOW
# ============================================================

def run_voice_workflow():

    try:

        dashboard_state["current_stage"] = (
            "Recording voice command"
        )

        dashboard_state["current_output"] = {
            "message": "Listening for voice command..."
        }

        result = record_voice()

        if not result["success"]:

            dashboard_state["current_stage"] = (
                "Voice command failed"
            )

            dashboard_state["current_output"] = {
                "message": result.get(
                    "message",
                    "Voice command failed."
                )
            }

            return

        recognized_text = result.get(
            "recognized_text",
            ""
        )

        command = result.get(
            "command"
        )

        score = result.get(
            "score",
            0
        )

        # ========================================================
            # DEBUG: CHECK DETECTED COMMAND
        # ========================================================

        print("\n========== DEBUG COMMAND ROUTING ==========")
        print("Recognized text:", recognized_text)
        print("Detected command:", command)
        print("Confidence score:", score)
        print("===========================================\n")


        dashboard_state["command"] = recognized_text

        # ----------------------------------------------------
        # HIGH CONFIDENCE
        # ----------------------------------------------------

        if command is not None and score >= 0.90:

            dashboard_state["needs_selection"] = False

            dashboard_state["needs_continue"] = True

            dashboard_state["needs_contract_check"] = False

            dashboard_state["current_stage"] = (
                "Command recognized - Continue processing"
            )

            dashboard_state["current_output"] = {

                "recognized_command":
                    recognized_text,

                "detected_task":
                    command,

                "confidence_score":
                    round(score, 2),

                "message":
                    "Command recognized successfully. "
                    "Click Continue Processing."
            }

            if (
                "Command recognized"
                not in dashboard_state["completed_steps"]
            ):

                dashboard_state["completed_steps"].append(
                    "Command recognized"
                )

            return

        # ----------------------------------------------------
        # LOW CONFIDENCE
        # ----------------------------------------------------

        dashboard_state["needs_continue"] = False

        dashboard_state["needs_selection"] = True

        dashboard_state["needs_contract_check"] = False

        dashboard_state["suggested_command"] = command

        dashboard_state["current_stage"] = (
            "Command requires confirmation"
        )

        dashboard_state["current_output"] = {

            "recognized_command":
                recognized_text,

            "detected_task":
                command or "Unknown",

            "confidence_score":
                round(score, 2),

            "message":
                "The agricultural task could not be "
                "identified confidently. Please select "
                "the intended task."
        }

    except Exception as e:

        dashboard_state["current_stage"] = (
            "Workflow error"
        )

        dashboard_state["current_output"] = {
            "error": str(e)
        }

    finally:

        dashboard_state["workflow_running"] = False


# ============================================================
# CONTRACT GENERATION
# ============================================================

def run_processing_workflow():

    try:

        dashboard_state["workflow_running"] = True

        result = process_recorded_command()

        if not result["success"]:

            dashboard_state["current_stage"] = (
                "Command processing failed"
            )

            dashboard_state["current_output"] = {
                "message":
                    result.get(
                        "message",
                        "Command processing failed"
                    )
            }

            return

        # Contract is already stored by web_controller.
        #
        # Do not verify here.
        #
        # The user must click CHECK CONTRACT.

    except Exception as e:

        dashboard_state["current_stage"] = (
            "Processing error"
        )

        dashboard_state["current_output"] = {
            "error": str(e)
        }

    finally:

        dashboard_state["workflow_running"] = False


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def dashboard():

    return render_template(
        "dashboard.html",
        farm=farm_state,
        state=dashboard_state
    )


@app.route("/resources")
def resources_page():
    resources = get_resources()
    history = get_resource_history()

    return render_template(
        "resources.html",
        resources=resources,
        history=history
    )


@app.route("/add_resource", methods=["POST"])
def add_resource_route():
    from flask import request, redirect, url_for, flash

    try:
        resource_name = request.form.get("resource", "").strip().lower()
        quantity_text = request.form.get("quantity", "").strip()

        if not quantity_text:
            raise ValueError("Please enter a quantity.")

        quantity = float(quantity_text)

        if not quantity > 0:
            raise ValueError("Quantity must be greater than zero.")

        add_resource(resource_name, quantity)

        # Refresh the in-memory farm state from SQLite
        saved_resources = get_resources()

        for name, details in saved_resources.items():
            farm_state["resources"][name] = details["quantity"]

        flash("Resource restocked successfully.", "success")

    except (ValueError, TypeError) as error:
        flash(str(error), "error")

    return redirect(url_for("resources_page"))

# ============================================================
# START VOICE
# ============================================================

@app.route("/start_voice")
def start_voice():

    if dashboard_state.get(
        "workflow_running",
        False
    ):

        return jsonify({

            "success": False,

            "message":
                "A workflow is already running."

        })

    dashboard_state["command"] = (
        "No command yet"
    )

    dashboard_state["current_stage"] = (
        "Starting voice workflow"
    )

    dashboard_state["current_output"] = {
        "message":
            "Starting voice command processing..."
    }

    dashboard_state["contract"] = None

    dashboard_state["task_id"] = "None"
    dashboard_state["agent"] = "None"
    dashboard_state["machine"] = "None"
    dashboard_state["task"] = "No task running"
    dashboard_state["crop"] = "None"
    dashboard_state["field"] = "None"

    dashboard_state["verification"] = (
        "Not verified"
    )

    dashboard_state["execution"] = (
        "Not executed"
    )

    dashboard_state["monitoring"] = (
        "Not started"
    )

    dashboard_state["multi_agent_verification"] = (
        "Not started"
    )

    dashboard_state["multi_agent_result"] = None  

    dashboard_state["execution_results"] = []
    dashboard_state["monitoring_results"] = []
    dashboard_state["recovery_results"] = []
    dashboard_state["workflow_activity"] = []
    dashboard_state["retry_monitoring_results"] = []

    dashboard_state["needs_selection"] = False

    dashboard_state["suggested_command"] = None

    dashboard_state["needs_continue"] = False

    dashboard_state["needs_contract_check"] = False

    dashboard_state["completed_steps"] = []

    dashboard_state["workflow_running"] = True

    dashboard_state["task_added"] = False

    thread = Thread(
        target=run_voice_workflow,
        daemon=True
    )

    thread.start()

    return jsonify({

        "success": True,

        "message":
            "Voice workflow started."

    })


# ============================================================
# CONTINUE PROCESSING
# ============================================================

@app.route("/continue_processing")
def continue_processing():

    if not dashboard_state.get(
        "needs_continue",
        False
    ):

        return jsonify({

            "success": False,

            "message":
                "There is no command waiting for processing."

        })

    if dashboard_state.get(
        "workflow_running",
        False
    ):

        return jsonify({

            "success": False,

            "message":
                "Processing is already running."

        })

    dashboard_state["needs_continue"] = False

    dashboard_state["current_stage"] = (
        "Starting task processing"
    )

    dashboard_state["current_output"] = {
        "message":
            "Starting task contract generation..."
    }

    thread = Thread(
        target=run_processing_workflow,
        daemon=True
    )

    thread.start()

    return jsonify({

        "success": True,

        "message":
            "Task processing started."

    })


# ============================================================
# CHECK CONTRACT
# ============================================================

@app.route("/check_contract")
def check_contract_route():

    if not dashboard_state.get(
        "needs_contract_check",
        False
    ):

        return jsonify({

            "success": False,

            "message":
                "There is no contract waiting for review."

        })

    if dashboard_state.get("workflow_running", False):
        return jsonify({
            "success": False,
            "message": "A workflow is already running."
        }), 409

    dashboard_state["workflow_running"] = True

    thread = Thread(
        target=run_contract_check,
        daemon=True
    )

    thread.start()

    return jsonify({

        "success": True,

        "message":
            "Contract verification started."

    })


def run_contract_check():

    try:

        check_contract()

    except Exception as e:

        dashboard_state["current_stage"] = (
            "Verification error"
        )

        dashboard_state["current_output"] = {
            "error": str(e)
        }

    finally:

        dashboard_state["workflow_running"] = False


# ADD VERIFIED TASK TO QUEUE
@app.route("/add_task")
def add_task_route():

    contract = dashboard_state.get("contract")

    if not contract:
        return jsonify({
            "success": False,
            "message": "No task contract is available."
        })

    if dashboard_state.get("verification") != "APPROVED":
        return jsonify({
            "success": False,
            "message": "Only an approved contract can be added."
        })

    success = add_task(contract)

    if not success:
        return jsonify({
            "success": False,
            "message": "Task could not be added to the queue."
        })

    dashboard_state["task_added"] = True
    dashboard_state["queue_count"] = get_task_count()
    dashboard_state["current_stage"] = "Task Added to Queue"

    dashboard_state["current_output"] = {
        "message": "Task added to queue successfully.",
        "task_id": contract.get("task_id"),
        "queue_count": get_task_count()
    }

    if "Task added to queue" not in dashboard_state["completed_steps"]:
        dashboard_state["completed_steps"].append(
            "Task added to queue"
        )

    return jsonify({
        "success": True,
        "message": "Task added to queue.",
        "queue_count": get_task_count()
    })


# ============================================================
# FINISH CURRENT TASK AND VERIFY ALL QUEUED CONTRACTS
# ============================================================

@app.route("/finish_tasks")
def finish_tasks():

    print("\n")
    print("=" * 60)
    print("DEBUG: FINISH TASK")
    print("=" * 60)

    # --------------------------------------------------------
    # Get the current contract shown on the dashboard
    # --------------------------------------------------------

    current_contract = dashboard_state.get("contract")

    if not current_contract:

        return jsonify({
            "success": False,
            "message":
                "No current task contract is available."
        })

    # --------------------------------------------------------
    # Current task must be verified before finishing
    # --------------------------------------------------------

    if dashboard_state.get("verification") != "APPROVED":

        return jsonify({
            "success": False,
            "message":
                "The current contract must be approved "
                "before finishing the task."
        })

    current_task_id = current_contract.get(
        "task_id"
    )

    print("Current task:", current_task_id)

    # --------------------------------------------------------
    # Check whether current task is already in the queue
    # --------------------------------------------------------

    task_already_queued = False

    for task in get_tasks():

        if task.get("task_id") == current_task_id:

            task_already_queued = True
            break

    # --------------------------------------------------------
    # If Add Task was NOT pressed, add the current task now
    # --------------------------------------------------------

    if not task_already_queued:

        print(
            "Current task is not in queue."
        )

        print(
            "Adding current task to queue..."
        )

        success = add_task(
            current_contract
        )

        if not success:

            return jsonify({
                "success": False,
                "message":
                    "Current task could not be "
                    "added to the queue."
            })

        dashboard_state["task_added"] = True

        dashboard_state["queue_count"] = (
            get_task_count()
        )

        print(
            "Current task added successfully."
        )

    else:

        print(
            "Current task is already in queue."
        )

    # --------------------------------------------------------
    # Show final queue before multi-agent verification
    # --------------------------------------------------------

    print("\nTasks currently in queue:")
    print(
        "Queue count:",
        get_task_count()
    )

    for task in get_tasks():

        print("\nTask ID:", task.get("task_id"))
        print("Agent:", task.get("agent"))
        print("Machine:", task.get("machine"))
        print("Task:", task.get("task"))
        print("Crop:", task.get("crop"))
        print("Field:", task.get("field"))

    print("=" * 60)
    print()

    # --------------------------------------------------------
    # Start multi-agent verification
    # --------------------------------------------------------

    if dashboard_state.get(
        "workflow_running",
        False
    ):

        return jsonify({
            "success": False,
            "message":
                "A workflow is already running."
        })

    dashboard_state["workflow_running"] = True

    dashboard_state["current_stage"] = (
        "Checking Multi-Agent Contracts"
    )

    dashboard_state["current_output"] = {

        "message":
            "Current task added. "
            "Checking all queued contracts "
            "for conflicts..."
    }

    thread = Thread(
        target=run_multi_agent_verification,
        daemon=True
    )

    thread.start()

    return jsonify({

        "success": True,

        "message":
            "Current task finished and "
            "multi-agent verification started.",

        "queue_count":
            get_task_count()
    })



def run_multi_agent_verification():
    try:
        result = verify_queued_tasks()

        dashboard_state["queue_count"] = get_task_count()
        dashboard_state["multi_agent_result"] = result
        dashboard_state["multi_agent_verification"] = result.get(
            "status", "UNKNOWN"
        )

        # Record multi-agent verification in Completed Steps
        if "Multi-agent verification completed" not in dashboard_state["completed_steps"]:
            dashboard_state["completed_steps"].append(
                "Multi-agent verification completed"
            )

        status = result.get("status", "UNKNOWN")

        if status == "APPROVED":
            message = "All queued tasks passed multi-agent verification."
        elif status == "PARTIALLY_APPROVED":
            message = "Some tasks passed verification. Blocked tasks will not execute."
        else:
            message = "The queued tasks failed multi-agent verification."

        dashboard_state["current_stage"] = "Multi-Agent Verification Complete"
        dashboard_state["current_output"] = {
            "message": message,
            "multi_agent_result": result
        }

        add_workflow_activity(
            f"Multi-agent verification completed: {status}"
        )

    except Exception as error:
        dashboard_state["multi_agent_verification"] = "ERROR"
        dashboard_state["current_stage"] = "Verification Error"
        dashboard_state["current_output"] = {
            "message": f"Multi-agent verification failed: {str(error)}"
        }

        add_workflow_activity(
            f"Multi-agent verification error: {str(error)}"
        )

    finally:
        dashboard_state["workflow_running"] = False


@app.route("/execute_tasks", methods=["POST"])
def execute_tasks():
    if dashboard_state.get("workflow_running"):
        return jsonify({
            "success": False,
            "message": "Another workflow is currently running."
        }), 409

    verification_result = dashboard_state.get("multi_agent_result")

    if not verification_result:
        return jsonify({
            "success": False,
            "message": "Verify the queued tasks before execution."
        }), 400

    status = verification_result.get("status")

    if status not in ["APPROVED", "PARTIALLY_APPROVED"]:
        return jsonify({
            "success": False,
            "message": "No tasks are approved for execution."
        }), 400

    dashboard_state["workflow_running"] = True

    if dashboard_state.get("execution") == "Completed":
        return jsonify({
            "success": False,
            "message": "These tasks have already been executed."
        }), 409
    dashboard_state["execution_results"] = []
    dashboard_state["monitoring_results"] = []
    dashboard_state["recovery_results"] = []
    dashboard_state["retry_monitoring_results"] = []

    try:
        for contract in get_tasks():
            task_id = contract.get("task_id", "UNKNOWN")
            task_status = contract.get("multi_agent_status", "Pending")

            # Never execute tasks that are blocked or still pending.
            if task_status != "APPROVED":
                dashboard_state["execution_results"].append({
                    "task_id": task_id,
                    "task": contract.get("task", "UNKNOWN"),
                    "success": False,
                    "skipped": True,
                    "failure_type": "multi_agent_conflict",
                    "message": "Task skipped because it was not approved."
                })

                add_workflow_activity(
                    f"Task {task_id} skipped: not approved."
                )
                continue

            try:
                # Execute the approved task.
                execution_result = execute_task(contract)
                # Save resource usage to the SQLite database.
                for resource_name, quantity in farm_state["resources"].items():
                    set_resource_quantity(resource_name, quantity)

                execution_result["task_id"] = task_id

                dashboard_state["execution_results"].append(
                    execution_result
                )

                add_workflow_activity(
                    f"Task {task_id}: execution "
                    f"{'successful' if execution_result.get('success') else 'failed'}."
                )

                # Monitor the result.
                monitoring_result = monitor_execution(
                    contract, execution_result
                )
                monitoring_result["task_id"] = task_id

                dashboard_state["monitoring_results"].append(
                    monitoring_result
                )

                if not monitoring_result.get("violation_detected"):
                    add_workflow_activity(
                        f"Task {task_id}: monitoring completed without violations."
                    )
                    continue

                add_workflow_activity(
                    f"Task {task_id}: monitoring detected a violation."
                )

                # Ask the recovery module what action to take.
                recovery_result = recover_from_violation(
                    contract,
                    execution_result,
                    monitoring_result
                )
                recovery_result["task_id"] = task_id

                dashboard_state["recovery_results"].append(
                    recovery_result
                )

                add_workflow_activity(
                    f"Task {task_id}: recovery action "
                    f"{recovery_result.get('action', 'unknown')} selected."
                )

                # Retry only when the recovery module requests it.
                if recovery_result.get("action") == "retry":
                    retry_result = execute_task(contract)
                    # Save resource usage after retry execution.
                    for resource_name, quantity in farm_state["resources"].items():
                        set_resource_quantity(resource_name, quantity)
                    retry_result["task_id"] = task_id
                    retry_result["is_retry"] = True

                    dashboard_state["execution_results"].append(
                        retry_result
                    )

                    retry_monitoring = monitor_execution(
                        contract, retry_result
                    )
                    retry_monitoring["task_id"] = task_id

                    dashboard_state["retry_monitoring_results"].append(
                        retry_monitoring
                    )

                    retry_succeeded = (
                        retry_result.get("success", False)
                        and not retry_monitoring.get("violation_detected", False)
                    )

                    recovery_result["retry_succeeded"] = retry_succeeded

                    add_workflow_activity(
                        f"Task {task_id}: retry "
                        f"{'succeeded' if retry_succeeded else 'did not resolve the issue'}."
                    )

            except Exception as error:
                dashboard_state["execution_results"].append({
                    "task_id": task_id,
                    "task": contract.get("task", "UNKNOWN"),
                    "success": False,
                    "skipped": False,
                    "failure_type": "execution_error",
                    "message": str(error)
                })

                add_workflow_activity(
                    f"Task {task_id}: execution error — {str(error)}"
                )

        
        # Mark execution and monitoring as completed
        dashboard_state["execution"] = "Completed"
        dashboard_state["monitoring"] = "Completed"

        # Update the Completed Steps checklist
        if "Task execution completed" not in dashboard_state["completed_steps"]:
            dashboard_state["completed_steps"].append(
                "Task execution completed"
            )

        if "Execution monitoring completed" not in dashboard_state["completed_steps"]:
            dashboard_state["completed_steps"].append(
                "Execution monitoring completed"
                )

        dashboard_state["current_stage"] = "Task Execution Complete"
        dashboard_state["current_output"] = {
            "message": "Execution and monitoring finished. Review the results below."
        }
        dashboard_state["current_output"] = {
            "message": "Execution and monitoring finished. Review the results below."
        }

        return jsonify({
            "success": True,
            "message": "Task execution and monitoring finished."
        })

    except Exception as error:
        dashboard_state["execution"] = "Failed"
        dashboard_state["current_stage"] = "Execution Error"
        dashboard_state["current_output"] = {
            "message": f"Execution workflow failed: {str(error)}"
        }

        add_workflow_activity(
            f"Execution workflow error: {str(error)}"
        )

        return jsonify({
            "success": False,
            "message": "The execution workflow failed."
        }), 500

    finally:
        dashboard_state["workflow_running"] = False


# ============================================================
# WORKFLOW STATUS
# ============================================================

@app.route("/workflow_status")
def workflow_status():
    dashboard_state["queue_count"] = get_task_count()

    dashboard_state["queued_tasks"] = [
        {
            "task_id": task.get("task_id", "UNKNOWN"),
            "task": task.get("task", "UNKNOWN"),
            "agent": task.get("agent", "UNKNOWN"),
            "machine": task.get("machine", "UNKNOWN"),
            "crop": task.get("crop", "UNKNOWN"),
            "field": task.get("field", "UNKNOWN"),
            "verification": task.get("verification", "Not verified"),
            "multi_agent_status": task.get(
                "multi_agent_status", "Pending"
            ),
            "conflict_reasons": task.get("conflict_reasons", [])
        }
        for task in get_tasks()
    ]

    dashboard_state.setdefault("execution_results", [])
    dashboard_state.setdefault("monitoring_results", [])
    dashboard_state.setdefault("recovery_results", [])
    dashboard_state.setdefault("workflow_activity", [])
    dashboard_state.setdefault("retry_monitoring_results", [])

    return jsonify(dashboard_state)

# ============================================================
# SELECT COMMAND
# ============================================================
@app.route(
    "/select_command",
    methods=["POST"]
)
def select_command():

    selected_command = request.form.get(
        "command"
    )

    # ========================================================
    # SAFETY CHECK:
    # Manual selection is allowed only when the system
    # actually requested it.
    # ========================================================

    if not dashboard_state.get(
        "needs_selection",
        False
    ):

        dashboard_state["current_stage"] = (
            "Manual selection not required"
        )

        dashboard_state["current_output"] = {
            "message":
                "Manual selection is not required. "
                "Continue processing the recognized command."
        }

        return redirect("/")

    # ========================================================
    # DEBUG: CHECK MANUAL SELECTION
    # ========================================================

    print("\n========== DEBUG MANUAL SELECTION ==========")

    print(
        "Browser submitted command:",
        selected_command
    )

    print(
        "needs_selection:",
        dashboard_state.get("needs_selection")
    )

    print(
        "needs_continue:",
        dashboard_state.get("needs_continue")
    )

    print(
        "=============================================\n"
    )

    # ========================================================
    # RESET MANUAL SELECTION STATE
    # ========================================================

    dashboard_state["needs_selection"] = False

    dashboard_state["suggested_command"] = None

    dashboard_state["needs_continue"] = False

    dashboard_state["needs_contract_check"] = False

    dashboard_state["workflow_running"] = True

    # ========================================================
    # UPDATE DASHBOARD
    # ========================================================

    dashboard_state["current_stage"] = (
        "Command identified"
    )

    dashboard_state["current_output"] = {

        "message":
            "User selected: "
            + selected_command

    }

    # ========================================================
    # PROCESS SELECTED COMMAND
    # ========================================================

    try:

        result = process_selected_command(
            selected_command
        )

        if not result["success"]:

            dashboard_state["current_stage"] = (
                "Command processing failed"
            )

            dashboard_state["current_output"] = {
                "message":
                    result.get(
                        "message",
                        "Command processing failed"
                    )
            }

        dashboard_state["workflow_running"] = False

    except Exception as e:

        dashboard_state["current_stage"] = (
            "Selection processing error"
        )

        dashboard_state["current_output"] = {
            "error": str(e)
        }

        dashboard_state["workflow_running"] = False

    # ========================================================
    # RETURN UPDATED DASHBOARD
    # ========================================================

    return redirect("/")


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=False
    )