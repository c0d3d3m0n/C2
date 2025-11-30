# C2 Framework

A custom Command & Control (C2) framework designed for offensive security simulations. This project consists of a central server built with FastAPI and a client-side CLI for managing agents and tasks.

## Features

- **Server**: 
  - Built with FastAPI for high performance.
  - SQLite database for persistent storage.
  - REST API for agent communication and management.
- **Client**:
  - Command-line interface (CLI) for easy interaction.
  - Supports registering agents, sending commands, and retrieving results.

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
Use the CLI tool to interact with the server. (Assuming `client/cli.py` is the entry point)
```bash
python client/cli.py --help
```

## Disclaimer
This tool is for educational and authorized testing purposes only. Misuse of this software is strictly prohibited.
