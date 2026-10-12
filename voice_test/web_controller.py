import sounddevice as sd
import whisper
import scipy.io.wavfile as wav

from nlp_preprocessing import preprocess_text
from command_failsafe import find_command
from task_contract_generator import generate_task_contract
from contract_verifier import verify_contract
from dashboard_state import dashboard_state


SAMPLE_RATE = 16000
DURATION = 8

model = whisper.load_model("base")


pending_command = {
    "recognized_text": "",
    "processed_tokens": [],
    "command": None,
    "score": 0
}


# ============================================================
# RECORD VOICE
# ============================================================

def record_voice():

    print("\nRecording voice command...")

    dashboard_state["current_stage"] = "Recording voice command"

    dashboard_state["current_output"] = {
        "message": "Listening for voice command..."
    }

    recording = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    wav.write(
        "command.wav",
        SAMPLE_RATE,
        recording
    )

    print("Recording complete.")

    dashboard_state["current_stage"] = "Recognizing voice command"

    dashboard_state["current_output"] = {
        "message": "Converting speech to text..."
    }

    result = model.transcribe(
        "command.wav",
        fp16=False
    )

    recognized_text = result["text"].strip()

    print("\nRecognized command:")
    print(recognized_text)

    if not recognized_text:

        dashboard_state["current_stage"] = "Waiting for voice command"

        dashboard_state["current_output"] = {
            "message": "No voice command was detected."
        }

        return {
            "success": False,
            "message": "No voice command was detected."
        }

    dashboard_state["command"] = recognized_text

    processed_tokens = preprocess_text(
        recognized_text
    )

    command, score = find_command(
        processed_tokens
    )

    pending_command["recognized_text"] = recognized_text
    pending_command["processed_tokens"] = processed_tokens
    pending_command["command"] = command
    pending_command["score"] = score

    dashboard_state["current_stage"] = "Command recognized"

    dashboard_state["current_output"] = {

        "recognized_command":
            recognized_text,

        "detected_task":
            command or "Unknown",

        "confidence_score":
            round(score, 2)

    }

    return {
        "success": True,
        "recognized_text": recognized_text,
        "command": command,
        "score": score
    }


# ============================================================
# GENERATE CONTRACT FOR CONFIDENT COMMAND
# ============================================================

def process_recorded_command():

    recognized_text = pending_command["recognized_text"]
    processed_tokens = pending_command["processed_tokens"]
    command = pending_command["command"]
    score = pending_command["score"]

    if not recognized_text:

        return {
            "success": False,
            "message": "No pending voice command is available."
        }

    if command is None or score < 0.55:

        dashboard_state["current_stage"] = (
            "Command requires clarification"
        )

        dashboard_state["current_output"] = {
            "message": "Command is unclear.",
            "confidence_score": round(score, 2)
        }

        return {
            "success": False,
            "message": "Command is unclear. Please select the intended task.",
            "needs_selection": True
        }

    if score < 0.90:

        dashboard_state["current_stage"] = (
            "Command requires confirmation"
        )

        dashboard_state["current_output"] = {
            "message":
                "Command could not be identified confidently.",
            "suggested_command": command,
            "confidence_score": round(score, 2)
        }

        return {
            "success": False,
            "message":
                "Command is unclear. Please select the intended task.",
            "needs_selection": True
        }

    return generate_and_prepare_contract(
        command
    )


# ============================================================
# GENERATE CONTRACT
# ============================================================

def generate_and_prepare_contract(selected_command):

    recognized_text = pending_command["recognized_text"]

    processed_tokens = pending_command["processed_tokens"]

    if not recognized_text:

        return {
            "success": False,
            "message":
                "No pending voice command is available."
        }

    print("\nGenerating task contract...")

    dashboard_state["current_stage"] = (
        "Generating Task Contract"
    )

    dashboard_state["current_output"] = {
        "message":
            "Generating formal task contract..."
    }

    contract = generate_task_contract(
        recognized_text,
        processed_tokens,
        selected_command
    )

    print("\nContract generated.")

    # Store contract
    dashboard_state["contract"] = contract

    dashboard_state["task_id"] = contract.get(
        "task_id",
        "None"
    )

    dashboard_state["agent"] = contract.get(
        "agent",
        "None"
    )

    dashboard_state["machine"] = contract.get(
        "machine",
        "None"
    )

    dashboard_state["task"] = contract.get(
        "task",
        "No task"
    )

    dashboard_state["crop"] = contract.get(
        "crop",
        "None"
    )

    dashboard_state["field"] = contract.get(
        "field",
        "None"
    )

    dashboard_state["verification"] = "Not verified"

    # Show generated contract
    dashboard_state["current_stage"] = (
        "Task Contract Generated"
    )

    dashboard_state["current_output"] = contract

    if (
        "Task contract generated"
        not in dashboard_state["completed_steps"]
    ):

        dashboard_state["completed_steps"].append(
            "Task contract generated"
        )

    # Wait for CHECK CONTRACT button
    dashboard_state["needs_contract_check"] = True

    return {
        "success": True,
        "recognized_text": recognized_text,
        "command": selected_command,
        "contract": contract
    }


# ============================================================
# CHECK / VERIFY CONTRACT
# ============================================================

def check_contract():

    contract = dashboard_state.get("contract")

    if not contract:

        return {
            "success": False,
            "message":
                "No generated contract is available."
        }

    print("\nChecking contract...")

    dashboard_state["needs_contract_check"] = False

    dashboard_state["current_stage"] = (
        "Verifying Contract"
    )

    dashboard_state["current_output"] = {
        "message":
            "Checking contract preconditions and constraints..."
    }

    verification_result = verify_contract(
        contract
    )

    print("\nContract verification completed.")

    if verification_result["verified"]:

        dashboard_state["verification"] = "APPROVED"

        dashboard_state["current_stage"] = (
            "Contract Verified and Approved"
        )

        dashboard_state["current_output"] = (
            verification_result
        )

        if (
            "Contract verified and approved"
            not in dashboard_state["completed_steps"]
        ):

            dashboard_state["completed_steps"].append(
                "Contract verified and approved"
            )

    else:

        dashboard_state["verification"] = "REJECTED"

        dashboard_state["current_stage"] = (
            "Contract Verification Failed"
        )

        dashboard_state["current_output"] = (
            verification_result
        )

        if (
            "Contract verification failed"
            not in dashboard_state["completed_steps"]
        ):

            dashboard_state["completed_steps"].append(
                "Contract verification failed"
            )

    return {
        "success": True,
        "verification": verification_result
    }


# ============================================================
# PROCESS SELECTED COMMAND
# ============================================================

def process_selected_command(selected_command):

    if selected_command not in [
        "harvest",
        "irrigate",
        "fertilizer"
    ]:

        return {
            "success": False,
            "message":
                "Invalid agricultural task selected."
        }

    print("\nUser selected command:")
    print(selected_command)

    dashboard_state["current_stage"] = (
        "Command identified"
    )

    dashboard_state["current_output"] = {

        "message":
            "User selected: "
            + selected_command
            + ". Generating task contract..."
    }

    return generate_and_prepare_contract(
        selected_command
    )