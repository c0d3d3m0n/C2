# C2 Client Usage Guide

This guide provides an overview of the commands available in the C2 Client CLI.

## Basic Usage

Run the CLI using python:
```bash
python client/cli.py [command] [arguments]
```

## Commands

### 1. List Agents
View all active agents connected to the server.
```bash
python client/cli.py agents
```

### 2. Execute Command
Execute a shell command on a specific agent.
```bash
python client/cli.py exec <agent_id> <command> [args...]
```
Example:
```bash
python client/cli.py exec 12345 whoami
python client/cli.py exec 12345 ls -la
```

### 3. List Tasks & Check Output
View the history of tasks for an agent.
By default, this only lists the tasks and their status.

```bash
python client/cli.py tasks <agent_id>
```

**[NEW] Show Output**
To view the output of completed tasks, use the `--show-output` (or `-o`) flag:
```bash
python client/cli.py tasks <agent_id> --show-output
# OR
python client/cli.py tasks <agent_id> -o
```

### 4. File Operations

**Upload File** (Server -> Agent)
```bash
python client/cli.py upload <agent_id> <local_file> <remote_path>
```

**Download File** (Agent -> Server)
```bash
python client/cli.py download <agent_id> <remote_path> <local_file_to_save>
```
*Note: This queues a download task. You must wait for it to complete.*

**Get Downloaded File**
Once a download task is complete, retrieve the file content:
```bash
python client/cli.py get-file <task_id> <local_file_path>
```

### 5. Helper Commands

**Get Agent ID**
Quickly get an agent ID for scripting or copy-pasting.
```bash
# Get the first agent ID
python client/cli.py get-id

# Get the most recent agent ID
python client/cli.py get-last-id
```
