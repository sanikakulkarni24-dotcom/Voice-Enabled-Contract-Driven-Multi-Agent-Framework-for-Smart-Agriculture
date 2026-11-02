
from farm_simulation import farm_state


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


def verify_multi_agent_contracts(contracts):
    conflicts = []
    task_statuses = {}
    conflict_reasons = {}

    approved_contracts = []
    blocked_contracts = []

    # Process tasks in their original order.
    for contract in contracts:
        task_id = contract.get("task_id", "UNKNOWN")
        task_statuses[task_id] = "APPROVED"
        conflict_reasons[task_id] = []

        current_agent = contract.get("agent")
        current_machine = contract.get("machine")
        current_field = normalize_field_name(
            contract.get("field")
        )
        current_task = str(
            contract.get("task", "")
        ).lower()
        current_crop = str(
            contract.get("crop", "")
        ).strip().lower()

        task_conflicts = []

        # Compare this task only with previously approved tasks.
        for previous in approved_contracts:
            previous_id = previous.get(
                "task_id", "UNKNOWN"
            )
            previous_agent = previous.get("agent")
            previous_machine = previous.get("machine")
            previous_field = normalize_field_name(
                previous.get("field")
            )
            previous_task = str(
                previous.get("task", "")
            ).lower()
            previous_crop = str(
                previous.get("crop", "")
            ).strip().lower()

            # Agent conflict.
            if (
                current_agent
                and current_agent == previous_agent
            ):
                task_conflicts.append({
                    "type": "agent_conflict",
                    "tasks": [previous_id, task_id],
                    "message": (
                        f"Agent '{current_agent}' is already "
                        f"assigned to approved task {previous_id}."
                    )
                })

            # Machine conflict.
            if (
                current_machine
                and current_machine == previous_machine
            ):
                task_conflicts.append({
                    "type": "machine_conflict",
                    "tasks": [previous_id, task_id],
                    "message": (
                        f"Machine '{current_machine}' is already "
                        f"assigned to approved task {previous_id}."
                    )
                })

            # Field conflicts: harvesting conflicts with another
            # operation on the same valid field.
            if (
                current_field
                and current_field == previous_field
                and current_field in farm_state["fields"]
                and (
                    "harvest" in current_task
                    or "harvest" in previous_task
                )
            ):
                task_conflicts.append({
                    "type": "field_conflict",
                    "tasks": [previous_id, task_id],
                    "field": current_field,
                    "message": (
                        f"Incompatible operations are assigned to "
                        f"{current_field}: {previous_id} and {task_id}."
                    )
                })

            # Duplicate operation: same task, crop and field.
            if (
                current_field
                and current_field == previous_field
                and current_field in farm_state["fields"]
                and current_task == previous_task
                and current_crop == previous_crop
            ):
                task_conflicts.append({
                    "type": "duplicate_task",
                    "tasks": [previous_id, task_id],
                    "field": current_field,
                    "message": (
                        f"{task_id} duplicates task {previous_id}: "
                        f"the same operation for the same crop "
                        f"and field was already approved."
                    )
                })

        if task_conflicts:
            task_statuses[task_id] = "BLOCKED"

            for conflict in task_conflicts:
                conflicts.append(conflict)
                conflict_reasons[task_id].append(
                    conflict["message"]
                )

            blocked_contracts.append(contract)
        else:
            approved_contracts.append(contract)

    task_results = []
    approved_tasks = []
    blocked_tasks = []

    for contract in contracts:
        task_id = contract.get("task_id", "UNKNOWN")

        task_result = {
            "task_id": task_id,
            "task": contract.get("task", "UNKNOWN"),
            "field": normalize_field_name(
                contract.get("field")
            ),
            "agent": contract.get("agent", "UNKNOWN"),
            "machine": contract.get("machine", "UNKNOWN"),
            "status": task_statuses[task_id],
            "conflict_reasons": conflict_reasons[task_id]
        }

        task_results.append(task_result)

        if task_result["status"] == "BLOCKED":
            blocked_tasks.append(task_result)
        else:
            approved_tasks.append(task_result)

    if not conflicts:
        overall_status = "APPROVED"
    elif approved_tasks:
        overall_status = "PARTIALLY_APPROVED"
    else:
        overall_status = "REJECTED"

    return {
        "verified": len(conflicts) == 0,
        "status": overall_status,
        "tasks": task_results,
        "approved_tasks": approved_tasks,
        "blocked_tasks": blocked_tasks,
        "conflicts": conflicts,
        "approved_count": len(approved_tasks),
        "blocked_count": len(blocked_tasks)
    }


def print_multi_agent_result(result):
    print("\n" + "=" * 50)
    print("MULTI-AGENT CONTRACT VERIFICATION")
    print("=" * 50)

    print(f"\nOverall Status: {result['status']}")
    print(f"Approved tasks: {result.get('approved_count', 0)}")
    print(f"Blocked tasks: {result.get('blocked_count', 0)}")

    for task in result.get("tasks", []):
        print(f"\nTask ID: {task['task_id']}")
        print(f"Task: {task['task']}")
        print(f"Status: {task['status']}")

        for reason in task.get("conflict_reasons", []):
            print(f"Reason: {reason}")

    if result.get("conflicts"):
        print("\nDetected conflicts:")

        for conflict in result["conflicts"]:
            print(
                f"- {conflict['type']}: "
                f"{conflict['message']}"
            )
    else:
        print("\nNo conflicts detected.")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    test_contracts = [
        {
            "task_id": "TASK-001",
            "agent": "Irrigation Agent",
            "machine": "Irrigation pump/system",
            "task": "Irrigate a field",
            "crop": "tomato",
            "field": "Field B"
        },
        {
            "task_id": "TASK-002",
            "agent": "Harvesting Agent",
            "machine": "Combine harvester",
            "task": "Harvest a mature crop",
            "crop": "wheat",
            "field": "Field A"
        },
        {
            "task_id": "TASK-003",
            "agent": "Harvesting Agent",
            "machine": "Combine harvester",
            "task": "Harvest a mature crop",
            "crop": "wheat",
            "field": "Field A"
        },
        {
            "task_id": "TASK-004",
            "agent": "Fertilizer Application Agent",
            "machine": "Tractor with fertilizer spreader",
            "task": "Apply fertilizer",
            "crop": "rice",
            "field": "Field C"
        }
    ]

    result = verify_multi_agent_contracts(test_contracts)
    print_multi_agent_result(result)
