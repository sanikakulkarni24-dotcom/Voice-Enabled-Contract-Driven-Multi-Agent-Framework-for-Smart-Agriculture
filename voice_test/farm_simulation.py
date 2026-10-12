# ------------------------------------------------
# FARM SIMULATION
# ------------------------------------------------

farm_state = {

    "farm_name": "Demo Farm",

    "weather": "clear",

    "fields": {

        "Field A": {
            "crop": "wheat",
            "soil_moisture": 40,
            "crop_maturity": 95,
            "status": "available"
        },

        "Field B": {
            "crop": "tomato",
            "soil_moisture": 25,
            "crop_maturity": 60,
            "status": "available"
        },

        "Field C": {
            "crop": "rice",
            "soil_moisture": 70,
            "crop_maturity": 85,
            "status": "available"
        }
    },

    "agents": {

        "Fertilizer Application Agent": {
            "status": "available",
            "machine": "Tractor with fertilizer spreader"
        },

        "Irrigation Agent": {
            "status": "available",
            "machine": "Irrigation pump/system"
        },

        "Harvesting Agent": {
            "status": "available",
            "machine": "Combine harvester"
        }
    },

    "machines": {

        "Tractor with fertilizer spreader": "available",

        "Irrigation pump/system": "available",

        "Combine harvester": "available"
    },

    "resources": {

        "fertilizer": 500,

        "water": 10000,

        "fuel": 500
    }
}


# ------------------------------------------------
# DISPLAY FARM STATE
# ------------------------------------------------

def display_farm_state():

    print(
        "\n" + "=" * 50
    )

    print(
        "SIMULATED FARM STATE"
    )

    print(
        "=" * 50
    )

    print(
        f"\nFarm: {farm_state['farm_name']}"
    )

    print(
        f"Weather: {farm_state['weather']}"
    )

    print("\nFIELDS")

    for field_name, field in farm_state[
        "fields"
    ].items():

        print(f"\n{field_name}")

        print(
            f"  Crop: {field['crop']}"
        )

        print(
            f"  Soil Moisture: "
            f"{field['soil_moisture']}%"
        )

        print(
            f"  Crop Maturity: "
            f"{field['crop_maturity']}%"
        )

        print(
            f"  Status: {field['status']}"
        )

    print("\nAGENTS")

    for agent_name, agent in farm_state[
        "agents"
    ].items():

        print(f"\n{agent_name}")

        print(
            f"  Status: {agent['status']}"
        )

        print(
            f"  Machine: {agent['machine']}"
        )

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

    print(
        "\n" + "=" * 50
    )


# ------------------------------------------------
# UPDATE FUNCTIONS
# ------------------------------------------------

def set_agent_status(
    agent_name,
    status
):

    if agent_name in farm_state["agents"]:

        farm_state["agents"][
            agent_name
        ]["status"] = status


def set_machine_status(
    machine_name,
    status
):

    if machine_name in farm_state["machines"]:

        farm_state["machines"][
            machine_name
        ] = status


def set_field_status(
    field_name,
    status
):

    if field_name in farm_state["fields"]:

        farm_state["fields"][
            field_name
        ]["status"] = status


def update_soil_moisture(
    field_name,
    moisture
):

    if field_name in farm_state["fields"]:

        farm_state["fields"][
            field_name
        ]["soil_moisture"] = moisture


def update_crop_maturity(
    field_name,
    maturity
):

    if field_name in farm_state["fields"]:

        farm_state["fields"][
            field_name
        ]["crop_maturity"] = maturity


def use_fertilizer(amount):

    if farm_state["resources"][
        "fertilizer"
    ] >= amount:

        farm_state["resources"][
            "fertilizer"
        ] -= amount

        return True

    return False


def use_water(amount):

    if farm_state["resources"][
        "water"
    ] >= amount:

        farm_state["resources"][
            "water"
        ] -= amount

        return True

    return False


def use_fuel(amount):

    if farm_state["resources"][
        "fuel"
    ] >= amount:

        farm_state["resources"][
            "fuel"
        ] -= amount

        return True

    return False


# ------------------------------------------------
# TEST
# ------------------------------------------------

if __name__ == "__main__":

    display_farm_state()