# Voice-Enabled Multi-Agent Framework for Contract-Based Task Planning and Verification in Smart Agriculture

## 1. Overview

The **Voice-Enabled Multi-Agent Framework for Contract-Based Task Planning and Verification in Smart Agriculture** is a Python-based prototype designed to simplify agricultural task management using voice commands.

The system allows users to issue farming instructions in natural language, such as irrigating a field, applying fertilizer, or harvesting crops. It processes the command, generates a structured task contract, verifies whether the task can be performed, checks compatibility with other queued tasks, and executes the approved task in a simulated farm environment.

The framework also includes execution monitoring, recovery handling, and persistent resource management using SQLite. These features help identify potential errors before execution, monitor task outcomes, and maintain resource quantities across application restarts.

**Note:** This is a simulation-based prototype. It does not directly control physical agricultural machinery or real farm equipment.

## 2. Problem Statement

Agricultural operations involve several activities, including irrigation, fertilizer application, and harvesting. These activities require suitable machines, sufficient resources, appropriate field conditions, and coordination between different operations.

Executing tasks without checking these conditions can lead to resource shortages, machine conflicts, unsuitable operations, and execution failures.

The proposed framework addresses these challenges by converting natural-language farming instructions into structured task contracts and validating them before execution. It also checks conflicts between queued tasks, monitors execution results, and provides a recovery mechanism when violations are detected.

## 3. Objectives

The main objectives of the project are:

- To accept agricultural instructions through voice commands.
- To convert recognized speech into structured task information.
- To generate task contracts using an AI language model and predefined rules.
- To verify task feasibility before execution.
- To identify conflicts between multiple agricultural agents.
- To simulate agricultural operations and update farm conditions.
- To monitor resource consumption and expected task outcomes.
- To support retry or abort decisions when execution violations occur.
- To maintain resource quantities and restocking history using SQLite.

## 4. Key Features

### 4.1 Voice Command Processing
Uses OpenAI Whisper to convert spoken agricultural instructions into text.

### 4.2 Natural Language Processing
Uses spaCy for text preprocessing, including tokenization and lemmatization, to support command interpretation.

### 4.3 AI-Based Task Contract Generation
Uses Llama 3 through Ollama, together with predefined task rules, to extract task details and represent agricultural operations as structured contracts.

### 4.4 Contract Verification
Checks whether a task satisfies the required conditions before it is allowed to proceed.

### 4.5 Multi-Agent Verification
Checks queued tasks for potential conflicts involving agents, machines, and fields.

### 4.6 Task Queue Management
Stores individually verified tasks until the system performs multi-agent compatibility checks.

### 4.7 Agricultural Task Simulation
Simulates fertilizer application, irrigation, and harvesting while updating the farm's state.

### 4.8 Execution Monitoring
Checks task results, resource consumption, machine status, field conditions, and expected effects.

### 4.9 Execution Recovery
Uses the execution violation information to select an appropriate retry or abort action.

### 4.10 Persistent Resource Management
Uses SQLite to store fertilizer, water, and fuel quantities. Users can restock resources through the web dashboard, view current quantities, and review restocking history. Resource quantities are also saved after task execution so that stored values can be restored when the application restarts.

## 5. Agricultural Agents

The framework contains three agricultural agents, each associated with a specific operation and machine.

| Agent | Associated Machine | Operation | Main Resource |
|---|---|---|---|
| Fertilizer Application Agent | Tractor with fertilizer spreader | Applies fertilizer to fields | Fertilizer and fuel |
| Irrigation Agent | Irrigation pump/system | Supplies water to fields | Water and fuel |
| Harvesting Agent | Combine harvester | Harvests mature crops | Fuel |

Each agent represents an agricultural operation in the simulated environment. The agents do not directly operate physical machines.

## 6. System Architecture and Workflow

The framework follows a staged workflow in which agricultural instructions are processed, verified, queued, executed, and monitored.

### Step 1: Voice Input
The user provides a farming instruction through the application's voice-input interface.

### Step 2: Speech Recognition
Whisper converts the spoken instruction into text.

### Step 3: NLP Preprocessing
spaCy preprocesses the recognized text to support command interpretation.

### Step 4: Task Contract Generation
The system identifies the intended operation and generates a structured task contract using Llama 3 and predefined task rules.

The contract represents the information required to process the requested agricultural task.

### Step 5: Contract Verification
The contract verifier checks the task's validity and feasibility, including applicable field conditions, crop requirements, machine availability, resource availability, preconditions, and constraints.

### Step 6: Task Queue Management
Tasks that pass individual verification are added to the task queue.

### Step 7: Multi-Agent Verification
The multi-agent verifier checks queued tasks for conflicts and compatibility issues before execution.

### Step 8: Task Execution
Tasks that pass the required checks are processed by the task executor. The agricultural operation is simulated using the farm's current state.

### Step 9: Farm and Resource Updates
The simulation updates relevant field conditions and resource quantities. Resource quantities are persisted in the SQLite database.

### Step 10: Execution Monitoring
The execution monitor checks whether the task's results and state changes match the expected outcomes.

### Step 11: Recovery Handling
If an execution violation is detected, the recovery mechanism selects a retry or abort action according to the available recovery logic.

### Workflow Summary

**Voice Input → Speech Recognition → NLP Preprocessing → Contract Generation → Contract Verification → Task Queue → Multi-Agent Verification → Task Execution → State and Resource Updates → Execution Monitoring → Recovery, if required**

## 7. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Programming Language | Python | Main application logic |
| Speech Recognition | OpenAI Whisper | Converts speech into text |
| NLP | spaCy (`en_core_web_sm`) | Text preprocessing |
| Language Model | Llama 3 | Assists with task information extraction |
| Local Model Runtime | Ollama | Runs the language model locally |
| Web Framework | Flask | Serves the dashboard and application routes |
| Database | SQLite | Stores resource quantities and restocking history |
| Data Representation | Python dictionaries and JSON | Represents farm state and structured task information |
| Frontend | HTML, CSS, JavaScript | Provides the dashboard and resource-management interface |
| Farm Simulation | Custom Python modules | Simulates agricultural operations |

## 8. Farm Simulation

The framework uses a custom Python simulation to represent farm fields, crops, machines, and resources.

The farm state contains information about field conditions and resource quantities. Agricultural operations modify this state according to the task being executed.

### Initial Farm Resources

The default resource quantities are:

| Resource | Initial Quantity | Unit |
|---|---:|---|
| Fertilizer | 500 | kg |
| Water | 10,000 | L |
| Fuel | 500 | L |

These quantities are used as the initial values when the SQLite resource database is created for the first time. Once resource quantities have been stored, subsequent initialization preserves the existing database values.

### Example Field State

The simulation includes fields with different crops and conditions.

| Field | Crop | Initial Moisture | Initial Maturity |
|---|---|---:|---:|
| Field A | Wheat | 40% | 95% |
| Field B | Tomato | 25% | 60% |
| Field C | Rice | 70% | 85% |

These values represent the initial example configuration and can be used to demonstrate how agricultural tasks affect the simulated farm.

## 9. Task Contract Generation and Verification

### 9.1 Task Contract Generation

The contract-generation component interprets the user's instruction and produces structured information describing the requested operation.

For example, the instruction "Irrigate Field B" identifies irrigation as the operation and Field B as the target field.

The system uses the language model alongside predefined task rules to support the extraction and representation of task information.

### 9.2 Contract Verification

Before execution, the contract verifier checks the conditions applicable to the requested operation. These checks may include:

- Whether the target field exists.
- Whether the requested operation is supported.
- Whether the crop and field conditions are suitable.
- Whether the required machine or agent is available.
- Whether sufficient resources are available.
- Whether the task satisfies the relevant preconditions and constraints.

A task that fails the required verification checks should not proceed through the normal approved execution workflow.

### 9.3 Multi-Agent Verification

Individual task verification does not necessarily guarantee that multiple tasks can be executed together.

The multi-agent verifier therefore examines the queued tasks to identify compatibility issues and potential conflicts involving agents, machines, and fields.

This additional verification stage helps prevent incompatible tasks from proceeding together.

## 10. Task Queue Management

The task queue acts as an intermediate stage between individual contract verification and task execution.

Its main responsibilities are:

- Collecting individually verified task contracts.
- Maintaining tasks awaiting multi-agent verification.
- Supporting compatibility checks across queued tasks.
- Allowing the application to coordinate multiple agricultural operations.

This approach separates the validation of an individual task from the verification of a group of tasks.

## 11. Task Execution

The task executor processes approved task contracts and invokes the corresponding agricultural operation in the simulation.

Examples include:

- Applying fertilizer to a target field.
- Supplying water through the irrigation operation.
- Harvesting a field when the required conditions are satisfied.

During execution, the system updates the simulated farm state and adjusts resource quantities according to the implemented operation logic.

After execution, the updated resource quantities are saved to SQLite so that they can be restored when the application is restarted.

## 12. Execution Monitoring and Recovery

### 12.1 Execution Monitoring

The execution monitor evaluates the outcome of an agricultural task against its expected behavior.

The monitoring process can examine relevant information such as:

- Machine status.
- Resource consumption.
- Changes in field conditions.
- Expected task effects.
- Execution violations.

Monitoring helps identify situations in which the task's actual outcome does not match the expected result.

### 12.2 Execution Recovery

When a violation is detected, the recovery component determines whether the task should be retried or aborted according to the implemented recovery logic.

The recovery mechanism is intended to handle execution problems rather than assume that every approved task will complete successfully.

**Current limitation:** Advanced retry-cost optimization and a formal retry budget are not implemented.

## 13. Persistent Resource Management Using SQLite

The resource-management module extends the framework by maintaining resource quantities beyond the lifetime of a single application session.

### 13.1 Database Structure

The SQLite database contains two main tables.

**Resources table**

Stores the current quantity and unit of each resource.

| Field | Description |
|---|---|
| `name` | Resource name |
| `quantity` | Current stored quantity |
| `unit` | Measurement unit |

**Resource history table**

Records successful restocking operations.

| Field | Description |
|---|---|
| `id` | Unique history record identifier |
| `resource_name` | Name of the restocked resource |
| `quantity_added` | Quantity added |
| `unit` | Measurement unit |
| `updated_at` | Date and time of restocking |

### 13.2 Restocking Resources

The dashboard provides a resource-management page where users can select a resource and enter the quantity to add.

The application validates the submitted quantity and resource selection before updating the database.

The restocking operation:

1. Validates the resource name.
2. Checks that the quantity is greater than zero.
3. Adds the quantity to the stored resource balance.
4. Records the restocking event in the history table.
5. Updates the in-memory farm resource state.
6. Displays a success or error message.

### 13.3 Resource Persistence

When the application starts, it initializes the database and loads the stored resource quantities into the simulated farm state.

After task execution, the updated quantities are written back to SQLite.

This ensures that resource quantities are not limited to temporary in-memory values. The database also retains restocking history for review through the dashboard.

### 13.4 Benefits

- Maintains resource quantities across application restarts.
- Supports restocking through the web interface.
- Provides a record of restocking operations.
- Connects resource availability with agricultural task execution.
- Makes the simulation easier to demonstrate and test.

**Important distinction:** The database stores resource quantities and restocking history. It does not represent real-time measurements from physical tanks, fuel sensors, or fertilizer storage equipment.

## 14. Web Dashboard

The application uses Flask to provide a browser-based interface for interacting with the framework.

The dashboard supports agricultural task interaction and provides access to the resource-management page.

The resource-management page includes:

- Current fertilizer, water, and fuel quantities.
- A form for selecting a resource and entering a restocking quantity.
- Success and error messages.
- A restocking history table.
- Navigation back to the main dashboard.

The dashboard provides a convenient way to demonstrate the system's features without interacting directly with the underlying Python modules.

## 15. Example End-to-End Scenario

Consider the instruction:

**"Irrigate Field B."**

The system processes this request through the following stages:

1. The user provides the instruction through the voice interface.
2. Whisper converts the spoken instruction into text.
3. spaCy preprocesses the recognized command.
4. The contract-generation component extracts the requested operation and target field.
5. The contract verifier checks the task against the applicable conditions and resource requirements.
6. If individual verification succeeds, the task is added to the queue.
7. The multi-agent verifier checks compatibility with other queued tasks.
8. If the required checks pass, the irrigation operation is executed in the simulated environment.
9. The simulation updates the field state and reduces the relevant resource quantities.
10. The updated resource quantities are saved in SQLite.
11. The execution monitor checks the result against the expected task effects.
12. If a violation is detected, the recovery component selects a retry or abort action according to its implemented logic.

This example demonstrates how the framework combines natural-language interaction, structured task representation, verification, simulation, resource persistence, and execution monitoring.

## 16. Project Structure

The following is the logical organization of the project. The exact files and directories in a local checkout may differ depending on the current implementation.

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
    ├── resource_database.py
    ├── templates/
    │   ├── dashboard.html
    │   └── resources.html
    └── static/
        └── style.css
```

### Main Modules

| Module | Responsibility |
|---|---|
| `app.py` | Flask application, routes, and resource-management integration |
| `voice_command.py` | Voice-command processing |
| `nlp_preprocessing.py` | Natural-language preprocessing |
| `command_failsafe.py` | Command safety or fallback handling |
| `task_contract_generator.py` | Task contract generation |
| `contract_verifier.py` | Individual task validation |
| `multi_agent_verifier.py` | Multi-agent task compatibility checks |
| `task_queue.py` | Task queue management |
| `task_executor.py` | Execution of approved agricultural tasks |
| `execution_monitor.py` | Monitoring of execution outcomes |
| `execution_recovery.py` | Recovery decisions for execution violations |
| `farm_simulation.py` | Simulated fields, farm conditions, and resource usage |
| `dashboard_state.py` | Dashboard-related state management |
| `web_controller.py` | Web interaction or control logic |
| `resource_database.py` | SQLite initialization, resource storage, restocking, and history |
| `templates/dashboard.html` | Main dashboard interface |
| `templates/resources.html` | Resource-management interface |
| `static/style.css` | Styling for the web interface |

## 17. Prerequisites

The following software and dependencies are required for a typical local setup:

- Windows 10 or later.
- Git.
- Python 3.13, subject to compatibility with the dependencies in `requirements.txt`.
- Ollama.
- Llama 3 model available through Ollama.
- FFmpeg.
- A microphone for live voice input.
- The spaCy English language model.

Python package versions should be taken from the project's `requirements.txt` file wherever versions are specified.

## 18. Installation and Setup

### Step 1: Clone the Repository

Run the following commands in PowerShell:

```powershell
git clone https://github.com/sanikakulkarni24-dotcom/Voice-Enabled-Contract-Driven-Multi-Agent-Framework-for-Smart-Agriculture.git
cd Voice-Enabled-Contract-Driven-Multi-Agent-Framework-for-Smart-Agriculture
```

If the repository URL or name changes, use the current URL displayed on the GitHub repository page.

### Step 2: Create a Virtual Environment

```powershell
py -3.13 -m venv venv
```

Activate the environment:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks environment activation, use the appropriate execution policy permitted on your machine or activate the environment using another supported terminal.

### Step 3: Install Python Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Install the spaCy English Model

```powershell
python -m spacy download en_core_web_sm
```

### Step 5: Install and Configure Ollama

Install Ollama from its official website:

https://ollama.com/

Download the Llama 3 model:

```powershell
ollama pull llama3
```

Ensure Ollama is running and the model is available before using the language-model functionality.

### Step 6: Install FFmpeg

Install FFmpeg using a trusted distribution for Windows and ensure that its executable is available through the system `PATH`.

Verify the installation:

```powershell
ffmpeg -version
```

### Step 7: Start the Application

If the repository contains the `voice_test` directory, navigate to it:

```powershell
cd voice_test
```

Start Flask:

```powershell
python app.py
```

Open the local address shown in the terminal. The usual Flask development address is:

http://127.0.0.1:5000

The actual address and port depend on the Flask configuration.

## 19. Using the Application

### Voice-Based Task Interaction

1. Start the Flask application.
2. Open the dashboard in a browser.
3. Provide a supported agricultural instruction using the voice interface.
4. Allow the system to process the recognized text.
5. Review the task-verification and execution results provided by the application.

### Resource Management

1. Open the main dashboard.
2. Select **Manage Resources**.
3. Review the current fertilizer, water, and fuel quantities.
4. Select the resource to restock.
5. Enter a positive quantity in the appropriate unit.
6. Submit the form.
7. Review the updated quantity and restocking history.

The resource quantities should persist when the Flask application is stopped and restarted, provided the same SQLite database file is used.

## 20. Example Voice Commands

The following examples illustrate the types of agricultural instructions supported by the project design:

- "Irrigate Field B."
- "Apply fertilizer to rice in Field C."
- "Harvest wheat in Field A."

The final result depends on the task-generation logic, available farm state, verification conditions, and implemented execution rules. A sample instruction should not be assumed to succeed if the task fails validation or violates applicable constraints.

## 21. Safety and Limitations

The current prototype has the following limitations:

- Agricultural operations are simulated rather than performed on physical equipment.
- Agents and machines are software representations.
- Field conditions and resource quantities are maintained by the simulation and SQLite database, not by live agricultural sensors.
- Task interpretation depends on speech recognition and language-model output.
- Predefined rules are used alongside language-model-based task information extraction.
- Multi-agent verification is limited to the checks implemented in the current verifier.
- The recovery mechanism supports the implemented retry and abort decisions; advanced retry-cost optimization and a formal retry budget are not implemented.
- The current SQLite resource history records restocking operations rather than providing a complete audit log of every resource consumption event.
- The local Flask development configuration is intended for demonstration and testing, not production deployment without additional security and configuration work.

## 22. Future Enhancements

Possible future improvements include:

- More extensive testing of task-contract correctness.
- Quantitative resource-allocation and conflict-checking strategies.
- Formal retry limits and resource-aware recovery decisions.
- Improved coordination and scheduling of multiple agents.
- More comprehensive logging of resource consumption and task execution.
- Integration with real agricultural sensors in a controlled environment.
- Integration with physical machinery through suitable control interfaces and safety mechanisms.
- Evaluation using measurable criteria such as task success rate, verification accuracy, conflict-detection performance, resource usage, and recovery outcomes.

These are potential extensions and should not be interpreted as features already implemented.

## 23. Research Relevance

The project provides a prototype for exploring contract-based task planning and verification in a multi-agent agricultural environment.

Its main research themes include:

- Natural-language interaction for agricultural task specification.
- Structured task contracts generated from user instructions.
- Pre-execution verification of task feasibility.
- Compatibility checking between multiple queued agricultural operations.
- Monitoring of simulated task execution.
- Recovery decisions when execution violations occur.
- Persistent management of agricultural resources.

Future research can evaluate the framework through controlled experiments that measure task-generation correctness, verification effectiveness, conflict detection, resource consumption, execution success, and recovery behavior.

## 24. Conclusion

The Voice-Enabled Multi-Agent Framework for Contract-Based Task Planning and Verification in Smart Agriculture demonstrates an approach to managing simulated agricultural operations through natural-language commands.

By combining speech recognition, NLP preprocessing, language-model-assisted task contract generation, individual contract verification, multi-agent verification, task execution, monitoring, recovery, and SQLite-based resource management, the framework provides an integrated environment for demonstrating agricultural task coordination.

The project serves as a foundation for further research into reliable, resource-aware, and coordinated agricultural task planning. Its current scope is limited to a software simulation, while real-world sensor integration, physical machinery control, and advanced resource-optimization methods remain areas for future development.
