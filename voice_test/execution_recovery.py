# ------------------------------------------------
# EXECUTION RECOVERY
# ------------------------------------------------


def recover_from_violation(
    contract,
    execution_result,
    monitoring_result
):

    print("\n" + "=" * 50)
    print("EXECUTION RECOVERY")
    print("=" * 50)

    violation_type = monitoring_result.get(
        "violation_type"
    )

    task_id = contract.get(
        "task_id",
        "UNKNOWN"
    )

    print(f"\nTask: {task_id}")

    print(
        f"\nViolation type: "
        f"{violation_type}"
    )


    # ------------------------------------------------
    # MACHINE FAILURE
    # ------------------------------------------------

    if violation_type == "machine_failure":

        print(
            "\nRecovery action:"
        )

        print(
            "Task cannot continue because "
            "the required machine is unavailable."
        )

        print(
            "\nRecovery decision: ABORT TASK"
        )

        return {
            "recovered": False,
            "action": "abort",
            "reason": "Machine unavailable"
        }


    # ------------------------------------------------
    # RESOURCE FAILURE
    # ------------------------------------------------

    if violation_type == "resource_failure":

        print(
            "\nRecovery action:"
        )

        print(
            "Required resource is unavailable."
        )

        print(
            "\nRecovery decision: ABORT TASK"
        )

        return {
            "recovered": False,
            "action": "abort",
            "reason": "Required resource unavailable"
        }


    # ------------------------------------------------
    # EFFECT / STATE FAILURE
    # ------------------------------------------------

    if violation_type == "state_effect_violation":

        print(
            "\nRecovery action:"
        )

        print(
            "Expected task effect was not achieved."
        )

        print(
            "\nRecovery decision: RETRY TASK"
        )

        return {
            "recovered": True,
            "action": "retry",
            "reason": "Expected effect was not achieved"
        }


    # ------------------------------------------------
    # GENERAL EXECUTION FAILURE
    # ------------------------------------------------

    if violation_type == "execution_failure":

        print(
            "\nRecovery action:"
        )

        print(
            "Execution failed unexpectedly."
        )

        print(
            "\nRecovery decision: ABORT TASK"
        )

        return {
            "recovered": False,
            "action": "abort",
            "reason": "Execution failure"
        }


    # ------------------------------------------------
    # UNKNOWN VIOLATION
    # ------------------------------------------------

    print(
        "\nUnknown violation type."
    )

    print(
        "\nRecovery decision: ABORT TASK"
    )

    return {
        "recovered": False,
        "action": "abort",
        "reason": "Unknown violation"
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
        "field": "Field A"
    }


    test_execution_result = {
        "success": True,
        "failure_type": None
    }


    test_monitoring_result = {
        "monitored": True,
        "violation_detected": True,
        "violation_type": "state_effect_violation",
        "violations": [
            "Expected crop effect was not achieved."
        ]
    }


    result = recover_from_violation(
        test_contract,
        test_execution_result,
        test_monitoring_result
    )


    print("\nRecovery Result:")
    print(result)
    