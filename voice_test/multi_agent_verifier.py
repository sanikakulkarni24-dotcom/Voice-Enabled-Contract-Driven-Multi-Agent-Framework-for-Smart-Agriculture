from farm_simulation import farm_state


# ------------------------------------------------
# FIELD NORMALIZATION
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
# CHECK DUPLICATE AGENTS
# ------------------------------------------------

def check_agent_conflicts(contracts, conflicts):

    agents_in_use = {}

    for contract in contracts:

        agent = contract.get("agent")
        task_id = contract.get(
            "task_id",
            "UNKNOWN"
        )

        if not agent:
            continue

        if agent in agents_in_use:

            previous_task = agents_in_use[agent]

            conflicts.append({
                "type": "agent_conflict",
                "tasks": [
                    previous_task,
                    task_id
                ],
                "message":
                    f"Agent '{agent}' is assigned to "
                    f"multiple tasks: "
                    f"{previous_task} and {task_id}."
            })

        else:

            agents_in_use[agent] = task_id


# ------------------------------------------------
# CHECK MACHINE CONFLICTS
# ------------------------------------------------

def check_machine_conflicts(
    contracts,
    conflicts
):

    machines_in_use = {}

    for contract in contracts:

        machine = contract.get("machine")

        task_id = contract.get(
            "task_id",
            "UNKNOWN"
        )

        if not machine:
            continue

        if machine in machines_in_use:

            previous_task = machines_in_use[
                machine
            ]

            conflicts.append({
                "type": "machine_conflict",
                "tasks": [
                    previous_task,
                    task_id
                ],
                "message":
                    f"Machine '{machine}' is required "
                    f"by multiple tasks: "
                    f"{previous_task} and {task_id}."
            })

        else:

            machines_in_use[machine] = task_id


# ------------------------------------------------
# CHECK FIELD CONFLICTS
# ------------------------------------------------

def check_field_conflicts(
    contracts,
    conflicts
):

    field_tasks = {}

    for contract in contracts:

        field = normalize_field_name(
            contract.get("field")
        )

        task_id = contract.get(
            "task_id",
            "UNKNOWN"
        )

        if not field:
            continue

        if field.lower() == "unknown":
            continue

        if field not in farm_state["fields"]:
            continue

        if field not in field_tasks:

            field_tasks[field] = []

        field_tasks[field].append(
            contract
        )

    for field, tasks in field_tasks.items():

        if len(tasks) < 2:
            continue

        for i in range(len(tasks)):

            for j in range(
                i + 1,
                len(tasks)
            ):

                task_1 = tasks[i]
                task_2 = tasks[j]

                task_1_id = task_1.get(
                    "task_id",
                    "UNKNOWN"
                )

                task_2_id = task_2.get(
                    "task_id",
                    "UNKNOWN"
                )

                operation_1 = str(
                    task_1.get(
                        "task",
                        ""
                    )
                ).lower()

                operation_2 = str(
                    task_2.get(
                        "task",
                        ""
                    )
                ).lower()

                # Harvesting conflicts with
                # another operation on the same field.

                if (
                    "harvest" in operation_1
                    or
                    "harvest" in operation_2
                ):

                    conflicts.append({
                        "type": "field_conflict",
                        "tasks": [
                            task_1_id,
                            task_2_id
                        ],
                        "field": field,
                        "message":
                            f"Multiple incompatible "
                            f"operations are assigned "
                            f"to {field}: "
                            f"{task_1_id} and "
                            f"{task_2_id}."
                    })


# ------------------------------------------------
# CHECK RESOURCE TYPE CONFLICTS
# ------------------------------------------------

def check_resource_conflicts(
    contracts,
    conflicts
):

    resource_usage = {}

    for contract in contracts:

        task_id = contract.get(
            "task_id",
            "UNKNOWN"
        )

        resources = contract.get(
            "required_resources",
            []
        )

        if isinstance(resources, str):

            resources = [resources]

        for resource in resources:

            resource_name = str(
                resource
            ).strip().lower()

            if resource_name not in resource_usage:

                resource_usage[
                    resource_name
                ] = []

            resource_usage[
                resource_name
            ].append(task_id)

    # At the current stage, resources such as
    # water, fertilizer and fuel are consumable
    # but their quantities are not specified
    # inside contracts.
    #
    # Therefore we do NOT reject tasks merely
    # because they share a resource.
    #
    # Quantity-based resource conflicts will
    # be added later when contracts contain
    # resource quantities.


# ------------------------------------------------
# VERIFY MULTIPLE CONTRACTS
# ------------------------------------------------

def verify_multi_agent_contracts(
    contracts
):

    conflicts = []

    if not contracts:

        return {
            "verified": True,
            "status": "APPROVED",
            "conflicts": []
        }

    check_agent_conflicts(
        contracts,
        conflicts
    )

    check_machine_conflicts(
        contracts,
        conflicts
    )

    check_field_conflicts(
        contracts,
        conflicts
    )

    check_resource_conflicts(
        contracts,
        conflicts
    )

    if len(conflicts) == 0:

        return {
            "verified": True,
            "status": "APPROVED",
            "conflicts": []
        }

    return {
        "verified": False,
        "status": "REJECTED",
        "conflicts": conflicts
    }


# ------------------------------------------------
# PRINT RESULT
# ------------------------------------------------
def print_multi_agent_result(
    result
):

    print(
        "\n" + "=" * 50
    )

    print(
        "MULTI-AGENT CONTRACT VERIFICATION"
    )

    print(
        "=" * 50
    )

    if result["verified"]:

        print(
            "\nMULTI-AGENT CONTRACTS VERIFIED"
        )

        print(
            "\nStatus: APPROVED"
        )

        print(
            "\nNo conflicts detected between "
            "the task contracts."
        )

    else:

        print(
            "\nMULTI-AGENT CONTRACT CONFLICT"
        )

        print(
            f"\nStatus: {result['status']}"
        )

        print(
            f"\nTotal conflicts detected: "
            f"{len(result['conflicts'])}"
        )

        print(
            "\nConflict details:"
        )

        for conflict in result["conflicts"]:

            print(
                "\n----------------------------------------"
            )

            print(
                f"Conflict type: "
                f"{conflict['type']}"
            )

            print(
                f"Tasks involved: "
                f"{', '.join(conflict['tasks'])}"
            )

            if "field" in conflict:

                print(
                    f"Field: "
                    f"{conflict['field']}"
                )

            print(
                f"Reason: "
                f"{conflict['message']}"
            )

        print(
            "\nExecution BLOCKED."
        )

        print(
            "No queued task will be executed."
        )

    print(
        "\n" + "=" * 50
    )

# ------------------------------------------------
# TEST
# ------------------------------------------------

if __name__ == "__main__":

    test_contracts = [

        {
            "task_id": "TASK-001",
            "agent": "Harvesting Agent",
            "machine": "Combine harvester",
            "task": "Harvest a mature crop",
            "crop": "wheat",
            "field": "Field A",
            "preconditions": [],
            "required_resources": [
                "fuel"
            ],
            "constraints": [],
            "expected_outcome":
                "Successful harvest"
        },

        {
            "task_id": "TASK-002",
            "agent": "Harvesting Agent",
            "machine": "Combine harvester",
            "task": "Harvest a mature crop",
            "crop": "tomato",
            "field": "Field B",
            "preconditions": [],
            "required_resources": [
                "fuel"
            ],
            "constraints": [],
            "expected_outcome":
                "Successful harvest"
        }
    ]

    result = verify_multi_agent_contracts(
        test_contracts
    )

    print_multi_agent_result(
        result
    )