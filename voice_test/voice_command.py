import sounddevice as sd
import whisper
import scipy.io.wavfile as wav
import time
from farm_simulation import farm_state

from nlp_preprocessing import preprocess_text
from command_failsafe import confirm_command
from task_contract_generator import (
    generate_task_contract,
    print_contract
)
from contract_verifier import (
    verify_contract,
    print_verification_result
)

from task_queue import (
    add_task,
    get_task_count,
    display_tasks,
    get_tasks
)

from multi_agent_verifier import (
    verify_multi_agent_contracts,
    print_multi_agent_result
)

from task_executor import (
    execute_task,
    display_execution_state
)

from execution_monitor import (
    monitor_execution
)

from execution_recovery import (
    recover_from_violation
)

SAMPLE_RATE = 16000
DURATION = 8


print("Loading Whisper model...")

model = whisper.load_model(
    "base"
)

print("Whisper loaded!")
# ------------------------------------------------
# DISPLAY FARM INFORMATION
# ------------------------------------------------

def display_command_information():

    print("\n" + "=" * 50)
    print("AVAILABLE FARM INFORMATION")
    print("=" * 50)

    print("\nAVAILABLE FIELDS")

    for field_name, field in farm_state["fields"].items():

        if field["status"] == "available":

            print(
                f"  {field_name} "
                f"-> Crop: {field['crop']}"
            )

    print("\nAVAILABLE AGENTS")

    for agent_name, agent in farm_state["agents"].items():

        if agent["status"] == "available":

            print(
                f"  {agent_name}"
            )
            print(
                f"    Machine: {agent['machine']}"
            )

    print("\nYou can give commands such as:")

    print("  - Harvest the wheat in Field A")
    print("  - Irrigate the tomato in Field B")
    print("  - Fertilize the rice in Field C")

    print("\nPlease read the available farm information.")
    print("Starting voice input in 10 seconds...")

    for seconds in range(10, 0, -1):

        print(
            f"  {seconds}...",
            end="\r"
        )

        time.sleep(1)

    print("\n")

# ------------------------------------------------
# MAIN COMMAND LOOP
# ------------------------------------------------

while True:

    print(
        "\n" + "=" * 50
    )

    print(
        "READY FOR AGRICULTURAL COMMAND"
    )

    print(
        "=" * 50
    )

    display_command_information()

    print(
        "\nSpeak your agricultural command..."
    )

    audio = sd.rec(
        int(
            DURATION *
            SAMPLE_RATE
        ),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16"
    )

    sd.wait()

    wav.write(
        "command.wav",
        SAMPLE_RATE,
        audio
    )

    print(
        "\nRecording complete!"
    )

    # ------------------------------------------------
    # SPEECH TO TEXT
    # ------------------------------------------------

    print(
        "Transcribing..."
    )

    result = model.transcribe(
        "command.wav"
    )

    recognized_text = (
        result["text"]
        .strip()
    )

    print(
        "\nRecognized command:"
    )

    print(
        recognized_text
    )

    # ------------------------------------------------
    # EMPTY COMMAND CHECK
    # ------------------------------------------------

    if not recognized_text:

        print(
            "\nNo speech detected."
        )

        print(
            "Please speak again."
        )

        continue

    # ------------------------------------------------
    # NLP PREPROCESSING
    # ------------------------------------------------

    processed_text = preprocess_text(
        recognized_text
    )

    print(
        "\nProcessed command:"
    )

    print(
        processed_text
    )

    if not processed_text:

        print(
            "\nNLP could not extract "
            "usable command tokens."
        )

        print(
            "Please speak again."
        )

        continue

    # ------------------------------------------------
    # FAILSAFE
    # ------------------------------------------------

    confirmation = confirm_command(
        recognized_text,
        processed_text
    )

    if not confirmation["confirmed"]:

        print(
            "\nCommand was not confirmed."
        )

        print(
            "Please speak the command again."
        )

        continue

    # ------------------------------------------------
    # CONFIRMED COMMAND
    # ------------------------------------------------

    print(
        "\nCommand confirmed."
    )

    suggested_command = (
        confirmation[
            "suggested_command"
        ]
    )

    confirmed_command = (
        confirmation[
            "command_text"
        ]
    )

    print(
        "\nConfirmed task:"
    )

    if suggested_command == "harvest":

        print(
            "Harvest the crop"
        )

    elif suggested_command == "irrigate":

        print(
            "Irrigate the field"
        )

    elif suggested_command == "fertilizer":

        print(
            "Apply fertilizer"
        )

    else:

        print(
            confirmed_command
        )

    # ------------------------------------------------
    # TASK CONTRACT GENERATION
    # ------------------------------------------------

    print(
        "\nGenerating task contract..."
    )

    contract = generate_task_contract(
        confirmed_command,
        processed_text,
        suggested_command
    )

    if contract is None:

        print(
            "\nTask contract generation failed."
        )

        print(
            "Please speak the command again."
        )

        continue

    print_contract(
        contract
    )

    # ------------------------------------------------
    # CONTRACT VERIFICATION
    # ------------------------------------------------

    print(
        "\nVerifying task contract..."
    )

    verification_result = verify_contract(
        contract
    )

    print_verification_result(
        verification_result
    )

    
    # ------------------------------------------------
    # ASK USER IF CONTRACT IS CORRECT
    # ------------------------------------------------

    if verification_result["verified"]:

        print(
            "\n" + "=" * 50
        )

        print(
            "CONTRACT GENERATED SUCCESSFULLY"
        )

        print(
            "=" * 50
        )

        print(
            "\nIs this contract correct?"
        )

        choice = input(
            "\nEnter Y for Yes or N for No: "
        ).strip().lower()

        # ------------------------------------------------
        # APPROVE CONTRACT AND ADD TO QUEUE
        # ------------------------------------------------

        if choice == "y":

            print(
                "\nContract confirmed by user."
            )

            # ------------------------------------------------
            # ADD CONTRACT TO TASK QUEUE
            # ------------------------------------------------

            add_task(
                contract
            )

            print(
                "\nTask added to queue."
            )

            print(
                f"Tasks currently in queue: "
                f"{get_task_count()}"
            )

            display_tasks()

            # ------------------------------------------------
            # ASK FOR ANOTHER COMMAND
            # ------------------------------------------------

            print(
                "\nDo you want to add another "
                "agricultural task?"
            )

            another_command = input(
                "\nEnter Y for Yes or N for No: "
            ).strip().lower()

            if another_command == "y":

                print(
                    "\nPreparing for the next "
                    "agricultural command..."
                )

                continue

            else:

                print(
                    "\nNo more tasks will be added."
                )

                # ------------------------------------------------
                # MULTI-AGENT CONTRACT VERIFICATION
                # ------------------------------------------------

                print(
                    "\nVerifying all queued tasks..."
                )

                multi_agent_result = (
                    verify_multi_agent_contracts(
                        get_tasks()
                    )
                )

                print_multi_agent_result(
                    multi_agent_result
                )

                # ------------------------------------------------
                # EXECUTE QUEUED TASKS
                # ------------------------------------------------

                if multi_agent_result["verified"]:

                    print(
                        "\nAll queued tasks are approved "
                        "for execution."
                    )

                    for contract in get_tasks():

                        print(
                            "\n" + "=" * 50
                        )

                        print(
                            f"EXECUTING "
                            f"{contract['task_id']}"
                        )

                        print(
                            "=" * 50
                        )

                        # ------------------------------------------------
                        # TASK EXECUTION
                        # ------------------------------------------------

                        execution_result = execute_task(
                            contract
                        )

                        # ------------------------------------------------
                        # DISPLAY UPDATED FARM STATE
                        # ------------------------------------------------

                        display_execution_state()

                        # ------------------------------------------------
                        # EXECUTION MONITORING
                        # ------------------------------------------------

                        monitoring_result = (
                            monitor_execution(
                                contract,
                                execution_result
                            )
                        )

                        # ------------------------------------------------
                        # EXECUTION RESULT
                        # ------------------------------------------------

                        if not execution_result["success"]:

                            print(
                                "\nTask execution failed."
                            )

                        else:

                            print(
                                "\nTask execution completed."
                            )


                        # ------------------------------------------------
                        # MONITORING RESULT
                        # ------------------------------------------------

                        if monitoring_result[
                            "violation_detected"
                        ]:

                            print(
                                "\nExecution completed with "
                                "contract violations."
                            )

                            print(
                                "\nViolation type:"
                            )

                            print(
                                monitoring_result.get(
                                    "violation_type",
                                    "unknown"
                                )
                            )


                            # ------------------------------------------------
                            # EXECUTION RECOVERY
                            # ------------------------------------------------

                            recovery_result = (
                                recover_from_violation(
                                    contract,
                                    execution_result,
                                    monitoring_result
                                )
                            )


                            # ------------------------------------------------
                            # RECOVERY DECISION
                            # ------------------------------------------------

                            if recovery_result[
                                "action"
                            ] == "retry":

                                print(
                                    "\nRecovery selected: "
                                    "Retry task."
                                )

                                print(
                                    "\nRe-executing task..."
                                )

                                # ------------------------------------------------
                                # RETRY EXECUTION
                                # ------------------------------------------------

                                retry_execution_result = execute_task(
                                    contract
                                )

                                # RETRY MONITORING
                                retry_monitoring_result = monitor_execution(
                                    contract,
                                    retry_execution_result
                                )

                                # ------------------------------------------------
                                # RETRY RESULT
                                # ------------------------------------------------

                                if (
                                    retry_execution_result["success"]
                                    and not retry_monitoring_result[
                                        "violation_detected"
                                    ]
                                ):
                                    print(
                                        "\nRECOVERY SUCCESSFUL"
                                    )

                                    print(
                                        "Task succeeded after retry."
                                    )
                                else:
                                    print(
                                        "\nRECOVERY FAILED"
                                    )
                                    print(
                                        "Task still violates the contract."
                                    )
                                    print(
                                        "\nRecovery decision: "
                                        "ABORT TASK"
                                    )
                            elif recovery_result["action"] == "abort":
                                print(
                                    "\nRecovery selected: "
                                    "Abort task."
                                )      
                        else:

                            print(
                                "\nExecution completed "
                                "without violations."
                            )

                    print(
                        "\n" + "=" * 50
                    )

                    print(
                        "ALL QUEUED TASKS PROCESSED"
                    )

                    print(
                        "=" * 50
                    )

                # ------------------------------------------------
                # MULTI-AGENT VERIFICATION FAILED
                # ------------------------------------------------

                else:

                    print(
                        "\nQueued tasks were rejected "
                        "due to multi-agent conflicts."
                    )

                    print(
                        "No tasks will be executed."
                    )

                break

        # ------------------------------------------------
        # REJECT CONTRACT
        # ------------------------------------------------

        else:

            print(
                "\nContract rejected by user."
            )

            print(
                "Please speak the command again."
            )

            continue

    # ------------------------------------------------
    # VERIFICATION FAILED
    # ------------------------------------------------

    else:

        print(
            "\nContract verification failed."
        )

        print(
            "Please speak the command again."
        )

        continue