from task_executor import execute_task
from execution_monitor import monitor_execution
from farm_simulation import farm_state


# ------------------------------------------------
# RESET FARM STATE
# ------------------------------------------------

def reset_farm():

    farm_state["fields"]["Field A"]["crop_maturity"] = 95
    farm_state["fields"]["Field A"]["soil_moisture"] = 40
    farm_state["fields"]["Field A"]["status"] = "available"

    farm_state["agents"]["Harvesting Agent"]["status"] = "available"

    farm_state["machines"]["Combine harvester"] = "available"

    farm_state["resources"]["fuel"] = 500
    farm_state["resources"]["water"] = 10000
    farm_state["resources"]["fertilizer"] = 500


# ------------------------------------------------
# TEST CONTRACT
# ------------------------------------------------

contract = {

    "task_id": "TASK-TEST",

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


# =================================================
# TEST 1 — MACHINE FAILURE
# =================================================

print("\n\n")
print("=" * 60)
print("TEST 1: MACHINE FAILURE")
print("=" * 60)

reset_farm()

execution_result = execute_task(
    contract,
    simulate_failure="machine"
)

monitoring_result = monitor_execution(
    contract,
    execution_result
)

print("\nMonitoring Result:")
print(monitoring_result)


# =================================================
# TEST 2 — RESOURCE VIOLATION
# =================================================

print("\n\n")
print("=" * 60)
print("TEST 2: RESOURCE VIOLATION")
print("=" * 60)

reset_farm()

execution_result = execute_task(
    contract,
    simulate_failure="resource"
)

monitoring_result = monitor_execution(
    contract,
    execution_result
)

print("\nMonitoring Result:")
print(monitoring_result)


# =================================================
# TEST 3 — STATE / EFFECT VIOLATION
# =================================================

print("\n\n")
print("=" * 60)
print("TEST 3: STATE / EFFECT VIOLATION")
print("=" * 60)

reset_farm()

execution_result = execute_task(
    contract,
    simulate_failure="effect"
)

monitoring_result = monitor_execution(
    contract,
    execution_result
)

print("\nMonitoring Result:")
print(monitoring_result)