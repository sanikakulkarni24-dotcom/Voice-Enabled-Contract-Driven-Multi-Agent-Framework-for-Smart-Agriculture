# ------------------------------------------------
# TASK QUEUE
# ------------------------------------------------

task_queue = []


# ------------------------------------------------
# ADD TASK
# ------------------------------------------------

def add_task(contract):

    if contract is None:
        return False

    task_queue.append(contract)

    return True


# ------------------------------------------------
# GET ALL TASKS
# ------------------------------------------------

def get_tasks():

    return task_queue


# ------------------------------------------------
# GET TASK COUNT
# ------------------------------------------------

def get_task_count():

    return len(task_queue)


# ------------------------------------------------
# DISPLAY TASKS
# ------------------------------------------------

def display_tasks():

    print("\n" + "=" * 50)
    print("TASK QUEUE")
    print("=" * 50)

    if not task_queue:

        print("\nNo tasks in queue.")

        print("\n" + "=" * 50)

        return

    for contract in task_queue:

        print(f"\nTask ID: {contract.get('task_id', 'UNKNOWN')}")

        print(f"Agent: {contract.get('agent', 'UNKNOWN')}")

        print(f"Machine: {contract.get('machine', 'UNKNOWN')}")

        print(f"Task: {contract.get('task', 'UNKNOWN')}")

        print(f"Crop: {contract.get('crop', 'unknown')}")

        print(f"Field: {contract.get('field', 'unknown')}")

        print(
            f"Resources: "
            f"{contract.get('required_resources', [])}"
        )

        print(
            f"Preconditions: "
            f"{contract.get('preconditions', [])}"
        )

        print(
            f"Constraints: "
            f"{contract.get('constraints', [])}"
        )

        print(
            f"Expected Outcome: "
            f"{contract.get('expected_outcome', 'UNKNOWN')}"
        )

        print("-" * 50)

    print("=" * 50)


# ------------------------------------------------
# REMOVE TASK
# ------------------------------------------------

def remove_task(task_id):

    for contract in task_queue:

        if contract.get("task_id") == task_id:

            task_queue.remove(contract)

            return True

    return False


# ------------------------------------------------
# CLEAR QUEUE
# ------------------------------------------------

def clear_queue():

    task_queue.clear()


# ------------------------------------------------
# VERIFY QUEUED TASKS
# ------------------------------------------------

def verify_queued_tasks():

    from multi_agent_verifier import (
        verify_multi_agent_contracts
    )

    contracts = get_tasks()

    return verify_multi_agent_contracts(contracts)


# ------------------------------------------------
# TEST
# ------------------------------------------------

if __name__ == "__main__":

    # ------------------------------------------------
    # TEST TASK 1
    # ------------------------------------------------

    test_task_1 = {

        "task_id": "TASK-001",

        "agent":
            "Harvesting Agent",

        "machine":
            "Combine harvester",

        "task":
            "Harvest a mature crop",

        "crop":
            "wheat",

        "field":
            "Field A",

        "required_resources":
            ["fuel"]
    }


    # ------------------------------------------------
    # TEST TASK 2
    # ------------------------------------------------

    test_task_2 = {

        "task_id": "TASK-002",

        "agent":
            "Irrigation Agent",

        "machine":
            "Irrigation pump/system",

        "task":
            "Irrigate a field",

        "crop":
            "tomato",

        "field":
            "Field B",

        "required_resources":
            ["water", "fuel"]
    }


    # ------------------------------------------------
    # ADD TASKS
    # ------------------------------------------------

    print("\nAdding tasks...")

    add_task(test_task_1)

    add_task(test_task_2)

    print(
        f"\nTotal tasks in queue: "
        f"{get_task_count()}"
    )


    # ------------------------------------------------
    # DISPLAY QUEUE
    # ------------------------------------------------

    display_tasks()


    # ------------------------------------------------
    # VERIFY QUEUED TASKS
    # ------------------------------------------------

    print("\nVerifying queued tasks...")

    result = verify_queued_tasks()

    from multi_agent_verifier import (
        print_multi_agent_result
    )

    print_multi_agent_result(result)


    # ------------------------------------------------
    # REMOVE TASK
    # ------------------------------------------------

    print("\nRemoving TASK-001...")

    remove_task("TASK-001")

    display_tasks()


    # ------------------------------------------------
    # CLEAR QUEUE
    # ------------------------------------------------

    print("\nClearing task queue...")

    clear_queue()

    display_tasks()

