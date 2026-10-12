# Voice-Enabled Multi-Agent Framework for Contract-Based Task Planning and Verification in Smart Agriculture

## Overview

This project presents a voice-enabled, multi-agent framework for agricultural task planning and execution. It converts natural-language farming commands into structured task contracts, verifies their feasibility, checks compatibility between multiple agents, and monitors task execution in a simulated farm environment.

The framework aims to reduce execution errors by validating agricultural tasks before execution and detecting violations during execution.

## Key Features

- **Voice Command Processing:** Converts spoken agricultural instructions into text using Whisper.
- **NLP Preprocessing:** Uses spaCy to tokenize and lemmatize commands.
- **AI-Based Contract Generation:** Uses Llama 3 through Ollama to extract task details and generate structured task contracts.
- **Contract Verification:** Checks field availability, crop requirements, agent and machine availability, resources, preconditions, and constraints.
- **Multi-Agent Verification:** Detects conflicts involving agents, machines, and fields across queued tasks.
- **Task Queue Management:** Collects individually verified tasks before multi-agent verification.
- **Task Execution:** Simulates agricultural operations and updates farm state and resource quantities.
- **Execution Monitoring:** Checks machine status, resource consumption, field state, and expected task effects.
- **Recovery Mechanism:** Selects retry or abort actions according to the detected execution violation.

## Agricultural Agents

| Agent | Machine | Operation |
|---|---|---|
| Fertilizer Application Agent | Tractor with fertilizer spreader | Applies fertilizer |
| Irrigation Agent | Irrigation pump/system | Irrigates fields |
| Harvesting Agent | Combine harvester | Harvests mature crops |

## System Workflow

1. The user provides an agricultural voice command.
2. Whisper converts speech into text.
3. spaCy preprocesses the recognized command.
4. The system identifies the operation and generates a structured task contract using Llama 3 and predefined task rules.
5. Contract verification checks whether the task satisfies the required conditions.
6. Approved contracts are added to the task queue.
7. Multi-agent verification checks for conflicts among queued tasks.
8. Tasks proceed to execution only if the queued contracts pass verification.
9. The simulated farm state and resources are updated.
10. Execution monitoring checks whether the task achieved its expected effects.
11. If a violation is detected, the recovery mechanism selects an appropriate action.

## Technology Stack

- **Programming Language:** Python
- **Speech Recognition:** OpenAI Whisper
- **NLP:** spaCy (`en_core_web_sm`)
- **Language Model:** Llama 3
- **Local Model Runtime:** Ollama
- **Web Framework:** Flask
- **Data Representation:** Python dictionaries and JSON
- **Farm Simulation:** Custom Python modules

## Project Structure

```text
smartagriculture/
├── requirements.txt
├── README.md
└── voice_test/
    ├── app.py
    ├── voice_command.py
    ├── nlp_preprocessing.py
    ├── command_failsafe.py
    ├── task_contract_generator.py
    ├── contract_verifier.py
    ├── multi_agent_verifier.py
    ├── task_queue.py
    ├── task_executor.py
    ├── execution_monitor.py
    ├── execution_recovery.py
    ├── farm_simulation.py
    ├── dashboard_state.py
    ├── web_controller.py
    ├── templates/
    └── static/
```

## Prerequisites

- Windows 10 or later
- Python 3.13, subject to dependency compatibility
- Git
- Ollama
- Llama 3 model
- FFmpeg
- A microphone for live voice input

## Installation and Setup

### 1. Clone the repository

```powershell
git clone https://github.com/sanikakulkarni24-dotcom/Voice-Enabled-Contract-Driven-Multi-Agent-Framework-for-Smart-Agriculture
cd Voice-Enabled-Contract-Driven-Multi-Agent-Framework-for-Smart-Agriculture
```

Replace the placeholders with your actual GitHub repository URL and repository name.

### 2. Create and activate a virtual environment

```powershell
py -3.13 -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install Python dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install the spaCy English model

```powershell
python -m spacy download en_core_web_sm
```

### 5. Set up Ollama and Llama 3

Install Ollama from its official website: https://ollama.com/

Then download the model:

```powershell
ollama pull llama3
```

Ensure Ollama is running before starting the application.

### 6. Install FFmpeg

Install FFmpeg and ensure that its executable is available through your system PATH. Whisper uses FFmpeg to process audio.

### 7. Run the application

```powershell
cd voice_test
python app.py
```

Open the local URL displayed in the Flask terminal, commonly:

http://127.0.0.1:5000

## Example Voice Commands

- "Irrigate Field B."
- "Apply fertilizer to rice in Field C."
- "Harvest wheat in Field A."

The system verifies the generated contracts before allowing tasks to proceed.

## Verification and Recovery

The framework uses three verification stages:

1. **Contract Verification:** Validates each task individually.
2. **Multi-Agent Verification:** Checks compatibility among queued tasks.
3. **Execution Monitoring:** Compares execution results and farm-state changes with expected outcomes.

When execution violations occur, the recovery module can select retry or abort according to the violation type.

## Scope and Limitations

- Agricultural operations run in a simulated farm environment.
- Agents and machines are software representations; the project does not directly control physical farm machinery.
- The current prototype uses predefined agricultural task rules alongside LLM-based information extraction.
- Retry-cost optimization and a formal retry budget are not currently implemented.
- Results depend on speech recognition quality and the correctness of the generated task information.

## Future Enhancements

- Quantitative resource allocation and conflict checking.
- Retry limits and resource-aware recovery decisions.
- More extensive testing of multi-agent task compatibility.
- Integration with real agricultural sensors and machinery in a controlled environment.

## License

No license has been specified yet. Add an appropriate open-source license if you intend to permit others to reuse or modify this project.
