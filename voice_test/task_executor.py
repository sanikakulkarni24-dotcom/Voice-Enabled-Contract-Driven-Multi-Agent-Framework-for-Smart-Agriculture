from farm_simulation import (
    farm_state,
    set_agent_status,
    set_machine_status,
    set_field_status,
    update_soil_moisture,
    update_crop_maturity,
    use_fertilizer,
    use_water,
    use_fuel
)


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
# CAPTURE EXECUTION STATE
# ------------------------------------------------

def capture_state(contract):

    field_name = normalize_field_name(
        contract.get("field")
    )

    agent = contract.get("agent")
    machine = contract.get("machine")

    state = {
        "resources": farm_state["resources"].copy(),
        "agent_status": None,
        "machine_status": None,
        "field_status": None,
        "soil_moisture": None,
        "crop_maturity": None
    }

    if agent in farm_state["agents"]:

        state["agent_status"] = farm_state[
            "agents"
        ][agent]["status"]

    if machine in farm_state["machines"]:

        state["machine_status"] = farm_state[
            "machines"
        ][machine]

    if field_name in farm_state["fields"]:

        field = farm_state["fields"][field_name]

        state["field_status"] = field["status"]
        state["soil_moisture"] = field["soil_moisture"]
        state["crop_maturity"] = field["crop_maturity"]

    return state


# ------------------------------------------------
# DISPLAY BEFORE / AFTER STATE
# ------------------------------------------------

def display_state_comparison(
    state_before,
    state_after
):

    print("\nBEFORE EXECUTION")
    print("-" * 30)

    print(
        f"Soil Moisture: "
        f"{state_before['soil_moisture']}%"
    )

    print(
        f"Crop Maturity: "
        f"{state_before['crop_maturity']}%"
    )

    print(
        f"Water: "
        f"{state_before['resources']['water']}"
    )

    print(
        f"Fertilizer: "
        f"{state_before['resources']['fertilizer']}"
    )

    print(
        f"Fuel: "
        f"{state_before['resources']['fuel']}"
    )

    print(
        f"Agent Status: "
        f"{state_before['agent_status']}"
    )

    print(
        f"Machine Status: "
        f"{state_before['machine_status']}"
    )

    print(
        f"Field Status: "
        f"{state_before['field_status']}"
    )

    print("\nAFTER EXECUTION")
    print("-" * 30)

    print(
        f"Soil Moisture: "
        f"{state_after['soil_moisture']}%"
    )

    print(
        f"Crop Maturity: "
        f"{state_after['crop_maturity']}%"
    )

    print(
        f"Water: "
        f"{state_after['resources']['water']}"
    )

    print(
        f"Fertilizer: "
        f"{state_after['resources']['fertilizer']}"
    )

    print(
        f"Fuel: "
        f"{state_after['resources']['fuel']}"
    )

    print(
        f"Agent Status: "
        f"{state_after['agent_status']}"
    )

    print(
        f"Machine Status: "
        f"{state_after['machine_status']}"
    )

    print(
        f"Field Status: "
        f"{state_after['field_status']}"
    )


# ------------------------------------------------
# HARVEST EXECUTION
# ------------------------------------------------

def execute_harvest(
    contract,
    simulate_failure=None
):

    agent = contract["agent"]
    machine = contract["machine"]

    field_name = normalize_field_name(
        contract["field"]
    )

    if field_name not in farm_state["fields"]:

        return {
            "success": False,
            "failure_type": "field_error",
            "message": f"Field not found: {field_name}"
        }

    field = farm_state["fields"][field_name]

    if field["crop_maturity"] < 90:

        return {
            "success": False,
            "failure_type": "precondition_failure",
            "message": (
                f"Harvesting cannot start. "
                f"{field_name} maturity is "
                f"{field['crop_maturity']}%"
            )
        }

    # --------------------------------------------
    # RESOURCE FAILURE SIMULATION
    # --------------------------------------------

    if simulate_failure == "resource":

        farm_state["resources"]["fuel"] = 0

        return {
            "success": False,
            "failure_type": "resource_failure",
            "message": (
                "Fuel became unavailable during "
                "harvesting."
            )
        }

    if not use_fuel(10):

        return {
            "success": False,
            "failure_type": "resource_failure",
            "message": "Insufficient fuel for harvesting."
        }

    set_agent_status(
        agent,
        "busy"
    )

    set_machine_status(
        machine,
        "busy"
    )

    set_field_status(
        field_name,
        "in progress"
    )

    print("\nHarvesting started...")
    print(f"Agent: {agent}")
    print(f"Machine: {machine}")
    print(f"Field: {field_name}")

    # --------------------------------------------
    # MACHINE FAILURE SIMULATION
    # --------------------------------------------

    if simulate_failure == "machine":

        set_machine_status(
            machine,
            "failed"
        )

        return {
            "success": False,
            "failure_type": "machine_failure",
            "message": (
                f"{machine} failed during harvesting."
            )
        }

    # --------------------------------------------
    # STATE / EFFECT FAILURE SIMULATION
    # --------------------------------------------

    if simulate_failure == "effect":

        print("\nSimulating effect failure...")
        print(
            "Harvest operation did not change "
            "crop maturity."
        )

        set_field_status(
            field_name,
            "available"
        )

        set_agent_status(
            agent,
            "available"
        )

        set_machine_status(
            machine,
            "available"
        )

        return {
            "success": True,
            "failure_type": None,
            "message": (
                "Harvesting operation completed, "
                "but expected effect was not produced."
            )
        }

    # --------------------------------------------
    # NORMAL HARVEST EFFECT
    # --------------------------------------------

    update_crop_maturity(
        field_name,
        0
    )

    set_field_status(
        field_name,
        "available"
    )

    set_agent_status(
        agent,
        "available"
    )

    set_machine_status(
        machine,
        "available"
    )

    return {
        "success": True,
        "failure_type": None,
        "message": (
            f"Harvesting completed successfully "
            f"in {field_name}."
        )
    }


# ------------------------------------------------
# IRRIGATION EXECUTION
# ------------------------------------------------

def execute_irrigation(
    contract,
    simulate_failure=None
):

    agent = contract["agent"]
    machine = contract["machine"]

    field_name = normalize_field_name(
        contract["field"]
    )

    if field_name not in farm_state["fields"]:

        return {
            "success": False,
            "failure_type": "field_error",
            "message": f"Field not found: {field_name}"
        }

    field = farm_state["fields"][field_name]

    if field["soil_moisture"] >= 70:

        return {
            "success": False,
            "failure_type": "precondition_failure",
            "message": (
                f"Irrigation not required. "
                f"{field_name} soil moisture is "
                f"{field['soil_moisture']}%."
            )
        }

    # --------------------------------------------
    # RESOURCE FAILURE SIMULATION
    # --------------------------------------------

    if simulate_failure == "resource":

        farm_state["resources"]["water"] = 0

        return {
            "success": False,
            "failure_type": "resource_failure",
            "message": (
                "Water became unavailable during "
                "irrigation."
            )
        }

    if not use_water(1000):

        return {
            "success": False,
            "failure_type": "resource_failure",
            "message": "Insufficient water for irrigation."
        }

    if not use_fuel(5):

        return {
            "success": False,
            "failure_type": "resource_failure",
            "message": "Insufficient fuel for irrigation."
        }

    set_agent_status(
        agent,
        "busy"
    )

    set_machine_status(
        machine,
        "busy"
    )

    set_field_status(
        field_name,
        "in progress"
    )

    print("\nIrrigation started...")
    print(f"Agent: {agent}")
    print(f"Machine: {machine}")
    print(f"Field: {field_name}")

    # --------------------------------------------
    # MACHINE FAILURE SIMULATION
    # --------------------------------------------

    if simulate_failure == "machine":

        set_machine_status(
            machine,
            "failed"
        )

        return {
            "success": False,
            "failure_type": "machine_failure",
            "message": (
                f"{machine} failed during irrigation."
            )
        }

    # --------------------------------------------
    # STATE / EFFECT FAILURE SIMULATION
    # --------------------------------------------

    if simulate_failure == "effect":

        print("\nSimulating effect failure...")
        print(
            "Irrigation operation did not increase "
            "soil moisture."
        )

        set_field_status(
            field_name,
            "available"
        )

        set_agent_status(
            agent,
            "available"
        )

        set_machine_status(
            machine,
            "available"
        )

        return {
            "success": True,
            "failure_type": None,
            "message": (
                "Irrigation operation completed, "
                "but expected effect was not produced."
            )
        }

    # --------------------------------------------
    # NORMAL IRRIGATION EFFECT
    # --------------------------------------------

    new_moisture = min(
        field["soil_moisture"] + 30,
        100
    )

    update_soil_moisture(
        field_name,
        new_moisture
    )

    set_field_status(
        field_name,
        "available"
    )

    set_agent_status(
        agent,
        "available"
    )

    set_machine_status(
        machine,
        "available"
    )

    return {
        "success": True,
        "failure_type": None,
        "message": (
            f"Irrigation completed successfully "
            f"in {field_name}. "
            f"Soil moisture is now "
            f"{new_moisture}%."
        )
    }


# ------------------------------------------------
# FERTILIZER EXECUTION
# ------------------------------------------------

def execute_fertilizer(
    contract,
    simulate_failure=None
):

    agent = contract["agent"]
    machine = contract["machine"]

    field_name = normalize_field_name(
        contract["field"]
    )

    if field_name not in farm_state["fields"]:

        return {
            "success": False,
            "failure_type": "field_error",
            "message": f"Field not found: {field_name}"
        }

    # --------------------------------------------
    # RESOURCE FAILURE SIMULATION
    # --------------------------------------------

    if simulate_failure == "resource":

        farm_state["resources"]["fertilizer"] = 0

        return {
            "success": False,
            "failure_type": "resource_failure",
            "message": (
                "Fertilizer became unavailable during "
                "fertilizer application."
            )
        }

    if not use_fertilizer(50):

        return {
            "success": False,
            "failure_type": "resource_failure",
            "message": "Insufficient fertilizer."
        }

    if not use_fuel(5):

        return {
            "success": False,
            "failure_type": "resource_failure",
            "message": (
                "Insufficient fuel for "
                "fertilizer application."
            )
        }

    set_agent_status(
        agent,
        "busy"
    )

    set_machine_status(
        machine,
        "busy"
    )

    set_field_status(
        field_name,
        "in progress"
    )

    print("\nFertilizer application started...")
    print(f"Agent: {agent}")
    print(f"Machine: {machine}")
    print(f"Field: {field_name}")

    # --------------------------------------------
    # MACHINE FAILURE SIMULATION
    # --------------------------------------------

    if simulate_failure == "machine":

        set_machine_status(
            machine,
            "failed"
        )

        return {
            "success": False,
            "failure_type": "machine_failure",
            "message": (
                f"{machine} failed during fertilizer "
                "application."
            )
        }

    set_field_status(
        field_name,
        "available"
    )

    set_agent_status(
        agent,
        "available"
    )

    set_machine_status(
        machine,
        "available"
    )

    return {
        "success": True,
        "failure_type": None,
        "message": (
            f"Fertilizer application completed "
            f"successfully in {field_name}."
        )
    }


# ------------------------------------------------
# MAIN TASK EXECUTOR
# ------------------------------------------------

def execute_task(
    contract,
    simulate_failure=None
):

    agent = contract.get("agent")

    print("\n" + "=" * 50)
    print("TASK EXECUTION")
    print("=" * 50)

    print(f"\nAgent: {agent}")
    print(f"Task: {contract.get('task')}")
    print(f"Field: {contract.get('field')}")
    print(f"Machine: {contract.get('machine')}")

    # --------------------------------------------
    # CAPTURE STATE BEFORE EXECUTION
    # --------------------------------------------

    state_before = capture_state(
        contract
    )

    # --------------------------------------------
    # EXECUTE TASK
    # --------------------------------------------

    if agent == "Harvesting Agent":

        result = execute_harvest(
            contract,
            simulate_failure
        )

    elif agent == "Irrigation Agent":

        result = execute_irrigation(
            contract,
            simulate_failure
        )

    elif agent == "Fertilizer Application Agent":

        result = execute_fertilizer(
            contract,
            simulate_failure
        )

    else:

        result = {
            "success": False,
            "failure_type": "unknown_agent",
            "message": f"Unknown agent: {agent}"
        }

    # --------------------------------------------
    # CAPTURE STATE AFTER EXECUTION
    # --------------------------------------------

    state_after = capture_state(
        contract
    )

    # --------------------------------------------
    # ADD EXECUTION INFORMATION
    # --------------------------------------------

    result["agent"] = agent

    result["machine"] = contract.get(
        "machine"
    )

    result["field"] = normalize_field_name(
        contract.get("field")
    )

    result["state_before"] = state_before

    result["state_after"] = state_after

    # --------------------------------------------
    # DISPLAY BEFORE / AFTER STATE
    # --------------------------------------------

    display_state_comparison(
        state_before,
        state_after
    )

    # --------------------------------------------
    # EXECUTION RESULT
    # --------------------------------------------

    print("\n" + "-" * 50)

    if result["success"]:

        print("EXECUTION SUCCESSFUL")
        print(result["message"])

    else:

        print("EXECUTION FAILED")
        print(result["message"])

    print("-" * 50)

    return result


# ------------------------------------------------
# DISPLAY UPDATED FARM STATE
# ------------------------------------------------

def display_execution_state():

    print("\n" + "=" * 50)
    print("UPDATED FARM STATE")
    print("=" * 50)

    print("\nFIELDS")

    for field_name, field in farm_state["fields"].items():

        print(f"\n{field_name}")
        print(f"  Crop: {field['crop']}")

        print(
            f"  Soil Moisture: "
            f"{field['soil_moisture']}%"
        )

        print(
            f"  Crop Maturity: "
            f"{field['crop_maturity']}%"
        )

        print(
            f"  Status: "
            f"{field['status']}"
        )

    print("\nAGENTS")

    for agent_name, agent in farm_state["agents"].items():

        print(f"\n{agent_name}")
        print(f"  Status: {agent['status']}")
        print(f"  Machine: {agent['machine']}")

    print("\nRESOURCES")

    print(
        f"  Fertilizer: "
        f"{farm_state['resources']['fertilizer']} kg"
    )

    print(
        f"  Water: "
        f"{farm_state['resources']['water']} L"
    )

    print(
        f"  Fuel: "
        f"{farm_state['resources']['fuel']} L"
    )

    print("\n" + "=" * 50)