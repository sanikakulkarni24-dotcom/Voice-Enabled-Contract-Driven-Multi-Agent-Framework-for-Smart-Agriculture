from farm_simulation import farm_state
# ------------------------------------------------
# FIELD NAME NORMALIZATION
# ------------------------------------------------

def normalize_field_name(field_name):

    if not field_name:
        return None

    field_name = str(field_name).strip()

    if field_name.lower().startswith("field "):

        letter = field_name[6:].strip().upper()

        if letter in ["A", "B", "C"]:
            return f"Field {letter}"

    if field_name.upper() in ["A", "B", "C"]:
        return f"Field {field_name.upper()}"

    return field_name


# ------------------------------------------------
# CHECK EXECUTION RESULT
# ------------------------------------------------

def check_execution_result(execution_result):

    if not execution_result:

        return (
            False,
            "No execution result was provided."
        )

    if not execution_result.get("success"):

        failure_type = execution_result.get(
            "failure_type"
        )

        message = execution_result.get(
            "message",
            "Task execution failed."
        )

        if failure_type == "machine_failure":

            return (
                False,
                f"Machine failure detected: {message}"
            )

        if failure_type == "resource_failure":

            return (
                False,
                f"Resource violation detected: {message}"
            )

        if failure_type == "effect_failure":

            return (
                False,
                f"State/effect violation detected: {message}"
            )

        return (
            False,
            f"Execution failure detected: {message}"
        )

    return True, None


# ------------------------------------------------
# CHECK MACHINE STATE AFTER EXECUTION
# ------------------------------------------------

def check_machine_state(contract):

    machine = contract.get("machine")

    if machine not in farm_state["machines"]:

        return (
            False,
            f"Machine violation: {machine} does not exist."
        )

    machine_status = farm_state["machines"][machine]

    if machine_status == "failed":

        return (
            False,
            f"Machine failure detected: "
            f"{machine} is in failed state."
        )

    return True, None


# ------------------------------------------------
# CHECK RESOURCE CONSUMPTION
# ------------------------------------------------

def check_resource_consumption(
    contract,
    execution_result
):

    state_before = execution_result.get(
        "state_before"
    )

    state_after = execution_result.get(
        "state_after"
    )

    if not state_before or not state_after:

        return (
            False,
            "Resource monitoring data is missing."
        )

    required_resources = contract.get(
        "required_resources",
        []
    )

    if isinstance(required_resources, str):

        required_resources = [
            required_resources
        ]

    for resource in required_resources:

        resource_name = str(
            resource
        ).strip().lower()

        if resource_name not in state_before["resources"]:
            continue

        before = state_before[
            "resources"
        ][resource_name]

        after = state_after[
            "resources"
        ][resource_name]

        if after < 0:

            return (
                False,
                f"Resource violation: "
                f"{resource_name} became negative."
            )

        if after > before:

            return (
                False,
                f"Resource violation: "
                f"{resource_name} increased unexpectedly."
            )

    return True, None


# ------------------------------------------------
# CHECK HARVEST EFFECT
# ------------------------------------------------

def check_harvest_effect(
    contract,
    execution_result
):

    if contract.get("agent") != "Harvesting Agent":

        return True, None

    state_before = execution_result.get(
        "state_before"
    )

    state_after = execution_result.get(
        "state_after"
    )

    if not state_before or not state_after:

        return (
            False,
            "Harvest effect monitoring data is missing."
        )

    before_maturity = state_before[
        "crop_maturity"
    ]

    after_maturity = state_after[
        "crop_maturity"
    ]

    # Successful harvesting should reduce
    # crop maturity to 0.

    if after_maturity != 0:

        return (
            False,
            "State/effect violation: "
            "harvesting completed but crop maturity "
            f"remained at {after_maturity}%."
        )

    if after_maturity >= before_maturity:

        return (
            False,
            "State/effect violation: "
            "crop maturity did not decrease "
            "after harvesting."
        )

    return True, None


# ------------------------------------------------
# CHECK IRRIGATION EFFECT
# ------------------------------------------------

def check_irrigation_effect(
    contract,
    execution_result
):

    if contract.get("agent") != "Irrigation Agent":

        return True, None

    state_before = execution_result.get(
        "state_before"
    )

    state_after = execution_result.get(
        "state_after"
    )

    if not state_before or not state_after:

        return (
            False,
            "Irrigation effect monitoring data is missing."
        )

    before_moisture = state_before[
        "soil_moisture"
    ]

    after_moisture = state_after[
        "soil_moisture"
    ]

    # Successful irrigation should increase
    # soil moisture.

    if after_moisture <= before_moisture:

        return (
            False,
            "State/effect violation: "
            "irrigation completed but soil moisture "
            f"did not increase from "
            f"{before_moisture}%."
        )

    return True, None


# ------------------------------------------------
# CHECK FIELD AFTER EXECUTION
# ------------------------------------------------

def check_field_state(contract):

    field_name = normalize_field_name(
        contract.get("field")
    )

    if field_name not in farm_state["fields"]:

        return (
            False,
            f"Field violation: "
            f"{field_name} does not exist."
        )

    field = farm_state["fields"][field_name]

    # After a normal completed task the field
    # should be available again.

    if field["status"] not in [
        "available",
        "in progress"
    ]:

        return (
            False,
            f"Field violation: "
            f"{field_name} has status "
            f"'{field['status']}'."
        )

    return True, None


# ------------------------------------------------
# MONITOR EXECUTION
# ------------------------------------------------

def monitor_execution(
    contract,
    execution_result
):

    print("\n" + "=" * 50)
    print("EXECUTION MONITORING")
    print("=" * 50)

    # ------------------------------------------------
    # CHECK PRIMARY EXECUTION FAILURE
    # ------------------------------------------------

    failure_type = execution_result.get(
        "failure_type"
    )

    # ------------------------------------------------
    # MACHINE FAILURE
    # ------------------------------------------------

    if failure_type == "machine_failure":

        message = execution_result.get(
            "message",
            "Machine failure occurred."
        )

        print("\nCONTRACT VIOLATION DETECTED")
        print(
            f"\n- Machine failure detected: "
            f"{message}"
        )

        return {
            "monitored": True,
            "violation_detected": True,
            "violation_type": "machine_failure",
            "violations": [
                f"Machine failure detected: {message}"
            ]
        }

    # ------------------------------------------------
    # RESOURCE FAILURE
    # ------------------------------------------------

    if failure_type == "resource_failure":

        message = execution_result.get(
            "message",
            "Resource became unavailable."
        )

        print("\nCONTRACT VIOLATION DETECTED")
        print(
            f"\n- Resource violation detected: "
            f"{message}"
        )

        return {
            "monitored": True,
            "violation_detected": True,
            "violation_type": "resource_failure",
            "violations": [
                f"Resource violation detected: {message}"
            ]
        }

    # ------------------------------------------------
    # OTHER EXECUTION FAILURE
    # ------------------------------------------------

    if not execution_result.get("success"):

        message = execution_result.get(
            "message",
            "Execution failed."
        )

        print("\nCONTRACT VIOLATION DETECTED")
        print(
            f"\n- Execution violation detected: "
            f"{message}"
        )

        return {
            "monitored": True,
            "violation_detected": True,
            "violation_type": "execution_failure",
            "violations": [
                f"Execution violation detected: {message}"
            ]
        }

    # ------------------------------------------------
    # SUCCESSFUL EXECUTION
    # NOW CHECK EXPECTED EFFECTS
    # ------------------------------------------------

    violations = []

    # Harvest effect

    passed, message = check_harvest_effect(
        contract,
        execution_result
    )

    if not passed:
        violations.append(message)

    # Irrigation effect

    passed, message = check_irrigation_effect(
        contract,
        execution_result
    )

    if not passed:
        violations.append(message)

    # ------------------------------------------------
    # MACHINE STATE
    # ------------------------------------------------

    passed, message = check_machine_state(
        contract
    )

    if not passed:
        violations.append(message)

    # ------------------------------------------------
    # FIELD STATE
    # ------------------------------------------------

    passed, message = check_field_state(
        contract
    )

    if not passed:
        violations.append(message)

    # ------------------------------------------------
    # RESOURCE CONSUMPTION
    # ------------------------------------------------

    passed, message = check_resource_consumption(
        contract,
        execution_result
    )

    if not passed:
        violations.append(message)

    # ------------------------------------------------
    # NO VIOLATIONS
    # ------------------------------------------------

    if not violations:

        print("\nEXECUTION MONITORING PASSED")
        print(
            "Execution remained consistent "
            "with the task contract."
        )

        return {
            "monitored": True,
            "violation_detected": False,
            "violation_type": None,
            "violations": []
        }

    # ------------------------------------------------
    # STATE / EFFECT VIOLATION
    # ------------------------------------------------

    print("\nCONTRACT VIOLATION DETECTED")

    for violation in violations:

        print(f"\n- {violation}")

    return {
        "monitored": True,
        "violation_detected": True,
        "violation_type": "state_effect_violation",
        "violations": violations
    }


# ------------------------------------------------
# TEST
# ------------------------------------------------

if __name__ == "__main__":

    test_contract = {

        "task_id": "TASK-001",

        "agent": "Harvesting Agent",

        "machine": "Combine harvester",

        "task": "Harvest a mature crop",

        "crop": "wheat",

        "field": "Field A",

        "priority": "high",

        "preconditions": [
            "field is ready for harvest"
        ],

        "required_resources": [
            "fuel"
        ],

        "constraints": [
            "avoid damaging crops"
        ],

        "expected_outcome":
            "Harvested wheat is ready for storage"
    }

    # This standalone test creates a simulated
    # successful execution result.

    execution_result = {

        "success": True,

        "failure_type": None,

        "message":
            "Harvesting completed successfully.",

        "state_before": {

            "soil_moisture": 40,

            "crop_maturity": 95,

            "resources": {
                "water": 10000,
                "fertilizer": 500,
                "fuel": 500
            },

            "agent_status": "available",

            "machine_status": "available",

            "field_status": "available"
        },

        "state_after": {

            "soil_moisture": 40,

            "crop_maturity": 0,

            "resources": {
                "water": 10000,
                "fertilizer": 500,
                "fuel": 490
            },

            "agent_status": "available",

            "machine_status": "available",

            "field_status": "available"
        }
    }

    result = monitor_execution(
        test_contract,
        execution_result
    )

    print("\nMonitoring Result:")
    print(result)

