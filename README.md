# C2 Framework

This project is a custom-built Command & Control (C2) framework designed specifically for offensive security research, red-team operations, and adversary simulation. It enables ethical hackers and security professionals to simulate real-world attacker infrastructure by establishing communication channels between distributed agents and a centralized command server.

## Features

- **Server**: 
  - Built with FastAPI for high performance.
  - SQLite database for persistent storage.
  - REST API for agent communication and management.
- **Client**:
  - Command-line interface (CLI) for easy interaction.
  - Supports registering agents, sending commands, and retrieving results.

## Understanding C2 Frameworks

Command & Control (C2) frameworks are the backbone of modern red team operations and adversary simulations. They allow operators to manage compromised systems remotely.

### Offensive Methodologies
1.  **Post-Exploitation**: Once access is gained, the agent (implant) is deployed to maintain persistence and execute further commands.
2.  **Beaconing**: Agents do not maintain a constant connection. Instead, they "beacon" home at set intervals (e.g., every 5 seconds) to check for tasks. This reduces network noise.
3.  **Jitter**: To evade detection, beacon intervals are randomized (jitter). A 5s interval with 10% jitter means the agent checks in between 4.5s and 5.5s.
4.  **Exfiltration**: Data is stolen from the target network, often chunked or encoded (e.g., Base64) to bypass DLP (Data Loss Prevention) systems.

### Defensive Methodologies
Defenders use C2 traffic analysis to identify compromises:
1.  **Traffic Analysis**: Looking for regular patterns (heartbeats) in network traffic.
2.  **Signature Detection**: Identifying known malicious binaries or byte sequences in memory.
3.  **Anomaly Detection**: Spotting unusual process behavior (e.g., `notepad.exe` making network connections).

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/c0d3d3m0n/C2.git
   cd C2
   ```

2. **Set up a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Server
Run the FastAPI server using uvicorn:
```bash
uvicorn server.main:app --reload
```
The server will start at `http://127.0.0.1:8000`.

### Using the Client
The client CLI supports connecting to both local and remote servers.

**Basic Usage:**
```bash
python client/cli.py <command> [args]
```

**Connecting to Remote Server:**
Use the `--url` flag to specify the remote server address (e.g., your Render deployment).
```bash
python client/cli.py --url https://your-app-name.onrender.com agents
```

**Available Commands:**
- `agents`: List active agents.
- `tasks <agent_id>`: List tasks for an agent.
- `exec <agent_id> <command> [args]`: Execute a shell command on an agent.
- `upload <agent_id> <local_file> <remote_path>`: Upload a file.
- `download <agent_id> <remote_path> <local_file>`: Download a file.
- `get-file <task_id> <local_file>`: Save a downloaded file from a task result.

## Disclaimer
This tool is for educational and authorized testing purposes only. Misuse of this software is strictly prohibited.
