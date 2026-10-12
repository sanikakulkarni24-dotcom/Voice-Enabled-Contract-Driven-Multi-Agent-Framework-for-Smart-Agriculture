from farm_simulation import farm_state


# ------------------------------------------------
# FIELD NAME NORMALIZATION
# ------------------------------------------------

def normalize_field_name(field_name):

    field_name = str(field_name).strip().lower()

    field_mapping = {
        "a": "Field A",
        "field a": "Field A",
        "b": "Field B",
        "field b": "Field B",
        "c": "Field C",
        "field c": "Field C"
    }

    return field_mapping.get(
        field_name,
        field_name
    )


# ------------------------------------------------
# FIELD VERIFICATION
# ------------------------------------------------

def verify_field(contract, errors):

    field_name = contract.get("field")

    if not field_name:

        errors.append(
            "Field is missing from contract."
        )

        return

    if str(field_name).lower() == "unknown":
        return

    field_name = normalize_field_name(
        field_name
    )

    if field_name not in farm_state["fields"]:

        errors.append(
            f"Field not found: {field_name}"
        )

        return

    field = farm_state["fields"][field_name]

    if field["status"] != "available":

        errors.append(
            f"{field_name} is currently "
            f"{field['status']}"
        )


# ------------------------------------------------
# CROP VERIFICATION
# ------------------------------------------------

def verify_crop(contract, errors):

    field_name = contract.get("field")

    crop = str(
        contract.get("crop", "unknown")
    ).lower()

    task = str(
        contract.get("task", "")
    ).lower()

    if not field_name:
        return

    if str(field_name).lower() == "unknown":
        return

    field_name = normalize_field_name(
        field_name
    )

    if field_name not in farm_state["fields"]:
        return

    field = farm_state["fields"][field_name]

    field_crop = field["crop"].lower()

    if crop != "unknown" and crop != field_crop:

        errors.append(
            f"Crop mismatch: contract specifies "
            f"{crop}, but {field_name} contains "
            f"{field_crop}"
        )

    if "harvest" in task:

        maturity = field["crop_maturity"]

        if maturity < 90:

            errors.append(
                f"Crop maturity is {maturity}%. "
                f"At least 90% maturity is required "
                f"for harvesting."
            )


# ------------------------------------------------
# AGENT VERIFICATION
# ------------------------------------------------

def verify_agent(contract, errors):

    agent_name = contract.get("agent")

    if not agent_name:

        errors.append(
            "Agent is missing from contract."
        )

        return

    if agent_name not in farm_state["agents"]:

        errors.append(
            f"Agent not found: {agent_name}"
        )

        return

    agent = farm_state["agents"][agent_name]

    if agent["status"] != "available":

        errors.append(
            f"{agent_name} is currently "
            f"{agent['status']}"
        )


# ------------------------------------------------
# MACHINE VERIFICATION
# ------------------------------------------------

def verify_machine(contract, errors):

    machine_name = contract.get("machine")

    if not machine_name:

        errors.append(
            "Machine is missing from contract."
        )

        return

    if machine_name not in farm_state["machines"]:

        errors.append(
            f"Machine not found: {machine_name}"
        )

        return

    machine_status = farm_state["machines"][
        machine_name
    ]

    if machine_status != "available":

        errors.append(
            f"{machine_name} is currently "
            f"{machine_status}"
        )


# ------------------------------------------------
# AGENT-MACHINE CROSS VERIFICATION
# ------------------------------------------------

def verify_agent_machine(contract, errors):

    agent_name = contract.get("agent")
    machine_name = contract.get("machine")

    if not agent_name or not machine_name:
        return

    if agent_name not in farm_state["agents"]:
        return

    expected_machine = farm_state[
        "agents"
    ][agent_name]["machine"]

    if machine_name != expected_machine:

        errors.append(
            f"Machine mismatch: {agent_name} "
            f"requires {expected_machine}, "
            f"but contract specifies {machine_name}"
        )


# ------------------------------------------------
# RESOURCE VERIFICATION
# ------------------------------------------------

def verify_resources(contract, errors):

    required_resources = contract.get(
        "required_resources",
        []
    )

    if isinstance(required_resources, str):

        required_resources = [
            required_resources
        ]

    available_resources = farm_state.get(
        "resources",
        {}
    )

    for resource in required_resources:

        resource_name = str(
            resource
        ).strip().lower()

        if resource_name in [
            str(machine).lower()
            for machine in farm_state["machines"]
        ]:

            errors.append(
                f"Machine '{resource}' should be "
                f"specified in the machine field, "
                f"not required_resources."
            )

            continue

        found = False

        for available_resource in available_resources:

            if (
                str(available_resource).lower()
                == resource_name
            ):

                quantity = available_resources[
                    available_resource
                ]

                found = True

                if quantity <= 0:

                    errors.append(
                        f"Resource unavailable: "
                        f"{resource}"
                    )

                break

        if not found:

            errors.append(
                f"Resource not available: "
                f"{resource}"
            )


# ------------------------------------------------
# AGENT-SPECIFIC RESOURCE VERIFICATION
# ------------------------------------------------

def verify_agent_resources(contract, errors):

    agent_name = contract.get("agent")

    required_resources = contract.get(
        "required_resources",
        []
    )

    if isinstance(required_resources, str):

        required_resources = [
            required_resources
        ]

    normalized_resources = [
        str(resource).strip().lower()
        for resource in required_resources
    ]

    expected_resources = {

        "Harvesting Agent": [
            "fuel"
        ],

        "Irrigation Agent": [
            "water",
            "fuel"
        ],

        "Fertilizer Application Agent": [
            "fertilizer",
            "fuel"
        ]
    }

    if agent_name not in expected_resources:
        return

    for resource in expected_resources[agent_name]:

        if resource.lower() not in normalized_resources:

            errors.append(
                f"Missing required resource "
                f"for {agent_name}: {resource}"
            )


# ------------------------------------------------
# PRECONDITION VERIFICATION
# ------------------------------------------------

def verify_preconditions(contract, errors):

    preconditions = contract.get(
        "preconditions",
        []
    )

    if isinstance(preconditions, str):

        preconditions = [
            preconditions
        ]

    for precondition in preconditions:

        condition = str(
            precondition
        ).lower()

        # Field existence
        if "field must exist" in condition:

            field_name = normalize_field_name(
                contract.get("field")
            )

            if field_name not in farm_state["fields"]:

                errors.append(
                    f"Precondition failed: "
                    f"{field_name} does not exist."
                )

        # Field availability
        elif "field must be available" in condition:

            field_name = normalize_field_name(
                contract.get("field")
            )

            if (
                field_name in farm_state["fields"]
                and farm_state["fields"][field_name]["status"]
                != "available"
            ):

                errors.append(
                    f"Precondition failed: "
                    f"{field_name} is not available."
                )

        # Crop match
        elif "crop must match field" in condition:

            field_name = normalize_field_name(
                contract.get("field")
            )

            crop = str(
                contract.get("crop", "unknown")
            ).lower()

            if (
                field_name in farm_state["fields"]
                and crop != "unknown"
                and farm_state["fields"][field_name]["crop"].lower()
                != crop
            ):

                errors.append(
                    "Precondition failed: "
                    "crop does not match field crop."
                )

        # Agent availability
        elif "agent must be available" in condition:

            agent_name = contract.get("agent")

            if (
                agent_name in farm_state["agents"]
                and farm_state["agents"][agent_name]["status"]
                != "available"
            ):

                errors.append(
                    f"Precondition failed: "
                    f"{agent_name} is not available."
                )

        # Specific agent availability
        elif "application agent must be available" in condition:

            agent_name = contract.get("agent")

            if (
                agent_name in farm_state["agents"]
                and farm_state["agents"][agent_name]["status"]
                != "available"
            ):

                errors.append(
                    f"Precondition failed: "
                    f"{agent_name} is not available."
                )

        # Machine availability
        elif "machine must be available" in condition:

            machine_name = contract.get("machine")

            if (
                machine_name in farm_state["machines"]
                and farm_state["machines"][machine_name]
                != "available"
            ):

                errors.append(
                    f"Precondition failed: "
                    f"{machine_name} is not available."
                )

        # Specific machine availability
        elif "pump/system must be available" in condition:

            machine_name = contract.get("machine")

            if (
                machine_name in farm_state["machines"]
                and farm_state["machines"][machine_name]
                != "available"
            ):

                errors.append(
                    f"Precondition failed: "
                    f"{machine_name} is not available."
                )

        elif "spreader must be available" in condition:

            machine_name = contract.get("machine")

            if (
                machine_name in farm_state["machines"]
                and farm_state["machines"][machine_name]
                != "available"
            ):

                errors.append(
                    f"Precondition failed: "
                    f"{machine_name} is not available."
                )

        # Resource availability
        elif "fuel must be available" in condition:

            if farm_state["resources"]["fuel"] <= 0:

                errors.append(
                    "Precondition failed: "
                    "fuel is unavailable."
                )

        elif "water must be available" in condition:

            if farm_state["resources"]["water"] <= 0:

                errors.append(
                    "Precondition failed: "
                    "water is unavailable."
                )

        elif "fertilizer must be available" in condition:

            if farm_state["resources"]["fertilizer"] <= 0:

                errors.append(
                    "Precondition failed: "
                    "fertilizer is unavailable."
                )


# ------------------------------------------------
# CONSTRAINT VERIFICATION
# ------------------------------------------------

def verify_constraints(contract, errors):

    constraints = contract.get(
        "constraints",
        []
    )

    if isinstance(constraints, str):

        constraints = [
            constraints
        ]

    field_name = normalize_field_name(
        contract.get("field")
    )

    if field_name not in farm_state["fields"]:
        return

    field = farm_state["fields"][field_name]

    for constraint in constraints:

        condition = str(
            constraint
        ).lower().strip()

        # Harvest maturity
        if condition == "crop_maturity >= 90":

            if field["crop_maturity"] < 90:

                errors.append(
                    f"Constraint violated: "
                    f"crop maturity is "
                    f"{field['crop_maturity']}%, "
                    f"but at least 90% is required."
                )

        # Irrigation moisture
        elif condition == "soil_moisture < 70":

            if field["soil_moisture"] >= 70:

                errors.append(
                    f"Constraint violated: "
                    f"soil moisture is "
                    f"{field['soil_moisture']}%, "
                    f"but it must be below 70%."
                )

        # Fertilizer
        elif condition == "fertilizer must be available":

            if farm_state["resources"]["fertilizer"] <= 0:

                errors.append(
                    "Constraint violated: "
                    "fertilizer is unavailable."
                )


# ------------------------------------------------
# MAIN VERIFICATION
# ------------------------------------------------

def verify_contract(contract):

    errors = []

    verify_field(
        contract,
        errors
    )

    verify_crop(
        contract,
        errors
    )

    verify_agent(
        contract,
        errors
    )

    verify_machine(
        contract,
        errors
    )

    verify_agent_machine(
        contract,
        errors
    )

    verify_resources(
        contract,
        errors
    )

    verify_agent_resources(
        contract,
        errors
    )

    verify_preconditions(
        contract,
        errors
    )

    verify_constraints(
        contract,
        errors
    )

    if len(errors) == 0:

        return {
            "verified": True,
            "status": "APPROVED",
            "errors": []
        }

    return {
        "verified": False,
        "status": "REJECTED",
        "errors": errors
    }


# ------------------------------------------------
# DISPLAY VERIFICATION RESULT
# ------------------------------------------------

def print_verification_result(result):

    print(
        "\n" + "=" * 50
    )

    print(
        "CONTRACT VERIFICATION"
    )

    print(
        "=" * 50
    )

    if result["verified"]:

        print(
            "\nCONTRACT VERIFIED"
        )

        print(
            "\nStatus: APPROVED"
        )

        print(
            "\nPreconditions: SATISFIED"
        )

        print(
            "Constraints: SATISFIED"
        )

        print(
            "\nAll verification checks passed."
        )

    else:

        print(
            "\nCONTRACT REJECTED"
        )

        print(
            f"\nStatus: {result['status']}"
        )

        print(
            "\nFailed checks:"
        )

        for error in result["errors"]:

            print(
                f"- {error}"
            )

    print(
        "\n" + "=" * 50
    )


# ------------------------------------------------
# TEST
# ------------------------------------------------

if __name__ == "__main__":

    test_contract = {

        "task_id": "TASK-TEST",

        "agent": "Irrigation Agent",

        "machine": "Irrigation pump/system",

        "task": "Irrigate a field",

        "crop": "tomato",

        "field": "B",

        "preconditions": [
            "field must exist",
            "field must be available",
            "crop must match field",
            "irrigation agent must be available",
            "irrigation pump/system must be available",
            "water must be available",
            "fuel must be available"
        ],

        "required_resources": [
            "water",
            "fuel"
        ],

        "constraints": [
            "soil_moisture < 70"
        ],

        "expected_outcome":
            "Soil moisture increases after irrigation"
    }

    result = verify_contract(
        test_contract
    )

    print_verification_result(
        result
    )