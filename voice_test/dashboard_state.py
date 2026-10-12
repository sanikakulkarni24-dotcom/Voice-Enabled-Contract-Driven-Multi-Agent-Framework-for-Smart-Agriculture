# Stores the live workflow information for the dashboard

dashboard_state = {

    # Latest voice command
    "command": "No command yet",

    # Command selected by the user
    "selected_command": None,

    # Current backend stage
    "current_stage": "Waiting for voice command",

    # Actual information/output produced by the current stage
    "current_output": None,

    # Complete generated contract
    "contract": None,

    # Task information
    "task_id": "None",
    "agent": "None",
    "machine": "None",
    "task": "No task running",
    "crop": "None",
    "field": "None",

    # Workflow results
    "verification": "Not verified",
    "execution": "Not executed",
    "monitoring": "Not started",

    # Completed workflow steps
    "completed_steps": [],

    # Selection state
    "needs_selection": False,
    "suggested_command": None,

    # Continue processing state
    "needs_continue": False,

    # Contract check state
    "needs_contract_check": False,

    # Background workflow state
    "workflow_running": False,

    "task_added": False,

    "queue_count": 0,

    "multi_agent_verification": "Not started",

    "multi_agent_result": None
}