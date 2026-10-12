import json
import re
import ollama


# ------------------------------------------------
# TASK ID COUNTER
# ------------------------------------------------

task_counter = 0


def generate_task_id():

    global task_counter

    task_counter += 1

    return f"TASK-{task_counter:03d}"


# ------------------------------------------------
# GENERATE TASK CONTRACT
# ------------------------------------------------

def generate_task_contract(
    command,
    processed_text,
    confirmed_task
):

    task_details = {

        "harvest": {

            "agent":
                "Harvesting Agent",

            "machine":
                "Combine harvester",

            "task":
                "Harvest a mature crop",

            "required_resources":
                ["fuel"],

            "preconditions": [
                "field must exist",
                "field must be available",
                "crop must match field",
                "crop maturity must be at least 90%",
                "harvesting agent must be available",
                "combine harvester must be available",
                "fuel must be available"
            ],

            "constraints": [
                "crop_maturity >= 90"
            ]
        },

        "irrigate": {

            "agent":
                "Irrigation Agent",

            "machine":
                "Irrigation pump/system",

            "task":
                "Irrigate a field",

            "required_resources":
                ["water", "fuel"],

            "preconditions": [
                "field must exist",
                "field must be available",
                "crop must match field",
                "irrigation agent must be available",
                "irrigation pump/system must be available",
                "water must be available",
                "fuel must be available"
            ],

            "constraints": [
                "soil_moisture < 70"
            ]
        },

        "fertilizer": {

            "agent":
                "Fertilizer Application Agent",

            "machine":
                "Tractor with fertilizer spreader",

            "task":
                "Apply fertilizer to a field",

            "required_resources":
                ["fertilizer", "fuel"],

            "preconditions": [
                "field must exist",
                "field must be available",
                "crop must match field",
                "fertilizer application agent must be available",
                "tractor with fertilizer spreader must be available",
                "fertilizer must be available",
                "fuel must be available"
            ],

            "constraints": []
        }
    }

    # ------------------------------------------------
    # CHECK CONFIRMED TASK
    # ------------------------------------------------

    if confirmed_task not in task_details:

        print(
            "\nInvalid confirmed task."
        )

        return None

    selected = task_details[
        confirmed_task
    ]

    # ------------------------------------------------
    # LLM PROMPT
    # ------------------------------------------------

    prompt = f"""
You are a smart agriculture task planning system.

The farmer's agricultural operation has already been confirmed
by the command failsafe system.

Confirmed operation:
{confirmed_task}

You MUST use this operation.

You MUST use the following agent:
{selected["agent"]}

You MUST use the following machine:
{selected["machine"]}

You MUST use the following task:
{selected["task"]}

You MUST use the following required resources:
{selected["required_resources"]}

The system will automatically assign the preconditions
and constraints after your response.

You only need to extract the crop and field from the
farmer's command.

The contract must contain exactly these fields:

- agent
- machine
- task
- crop
- field
- preconditions
- required_resources
- constraints
- expected_outcome

IMPORTANT RULES:

1. The confirmed operation MUST NOT be changed.

2. The agent MUST be:
{selected["agent"]}

3. The machine MUST be:
{selected["machine"]}

4. The task MUST be:
{selected["task"]}

5. required_resources MUST be:
{selected["required_resources"]}

6. The machine MUST NOT be placed inside required_resources.

7. required_resources must contain ONLY actual consumable resources.

8. Extract the crop from the farmer's command.

9. Extract the field from the farmer's command.

10. If the crop is not provided, use "unknown".

11. If the field is not provided, use "unknown".

12. Do NOT generate priority.

13. Do NOT generate preconditions.

14. Do NOT generate constraints.

15. expected_outcome must be a string.

16. Do NOT use null.

17. Return ONLY valid JSON.

18. Do NOT use Markdown.

19. Do NOT use code fences.

20. Do NOT provide explanations before or after the JSON.

Original farmer command:
{command}

spaCy preprocessed command:
{processed_text}
"""

    # ------------------------------------------------
    # CALL LLAMA
    # ------------------------------------------------

    response = ollama.chat(

        model="llama3",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    response_text = (
        response["message"]["content"]
        .strip()
    )

    # ------------------------------------------------
    # FUNCTION TO FINALIZE CONTRACT
    # ------------------------------------------------

    def finalize_contract(contract):

        finalized_contract = {
            "task_id": generate_task_id(),

            "agent": selected["agent"],
            "machine": selected["machine"],
            "task": selected["task"],

            "crop": contract.get("crop", "unknown"),
            "field": contract.get("field", "unknown"),

            "preconditions": selected["preconditions"],

            "required_resources": selected["required_resources"],

            "constraints": selected["constraints"],

            "expected_outcome": contract.get(
                "expected_outcome",
                "Task completed successfully"
            )
        }

        return finalized_contract

    # ------------------------------------------------
    # NORMAL JSON
    # ------------------------------------------------

    try:

        contract = json.loads(
            response_text
        )

        return finalize_contract(contract)

    except json.JSONDecodeError:

        pass

    # ------------------------------------------------
    # REMOVE MARKDOWN
    # ------------------------------------------------

    cleaned_text = re.sub(
        r"```json\s*",
        "",
        response_text,
        flags=re.IGNORECASE
    )

    cleaned_text = re.sub(
        r"```\s*",
        "",
        cleaned_text
    )

    cleaned_text = cleaned_text.strip()

    # ------------------------------------------------
    # CLEANED JSON
    # ------------------------------------------------

    try:

        contract = json.loads(
            cleaned_text
        )

        return finalize_contract(contract)

    except json.JSONDecodeError:

        pass

    # ------------------------------------------------
    # EXTRACT JSON OBJECT
    # ------------------------------------------------

    start = cleaned_text.find("{")
    end = cleaned_text.rfind("}")

    if start != -1 and end != -1:

        json_text = cleaned_text[
            start:end + 1
        ]

        try:

            contract = json.loads(
                json_text
            )

            return finalize_contract(contract)

        except json.JSONDecodeError:

            pass

    # ------------------------------------------------
    # FAILURE
    # ------------------------------------------------

    print(
        "\nLlama returned invalid JSON."
    )

    print(
        "\nRaw Llama response:"
    )

    print(
        response_text
    )

    return None


# ------------------------------------------------
# PRINT CONTRACT
# ------------------------------------------------

def print_contract(contract):

    print(
        "\n" + "=" * 50
    )

    print(
        "GENERATED TASK CONTRACT"
    )

    print(
        "=" * 50
    )

    print(
        json.dumps(
            contract,
            indent=4
        )
    )

    print(
        "=" * 50
    )