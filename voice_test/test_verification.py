from contract_verifier import verify_contract
from contract_verifier import print_verification_result


contract = {
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
        "Combine harvester",
        "fuel",
        "operators"
    ],
    "constraints": [
        "avoid damaging crops"
    ],
    "expected_outcome": "Harvested wheat is ready for storage"
}


result = verify_contract(contract)

print_verification_result(result)