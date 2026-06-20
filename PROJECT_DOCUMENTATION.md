# C2 Framework Project Documentation

## 1. Project Overview

This repository contains a lightweight command-and-control style application built with FastAPI, SQLAlchemy, SQLite, and a Python-based CLI/agent pair. The project is structured around three cooperating parts:

- `server/` exposes the HTTP API and persists operational state.
- `client/` provides an operator-facing CLI for interacting with the server.
- `agent/` contains a beaconing implant that registers, polls for tasks, executes them, and submits results.

The application is intentionally small and easy to understand. It is suitable for local experimentation, protocol research, and studying how a task queue, beacon loop, and result collection flow can be implemented in Python.

## 2. Repository Structure

Top-level files and directories:

- `server/` - FastAPI server, database layer, SQLAlchemy models, and Pydantic schemas.
- `client/` - Command-line tool used by an operator to manage agents and queue tasks.
- `agent/` - The polling agent that registers with the server and executes tasks.
- `requirements.txt` - Python dependencies.
- `Dockerfile` - Container build definition for the server.
- `render.yaml` - Render deployment configuration.
- `README.md` - High-level project overview.
- `USAGE.md` - Client usage reference.
- `DEPLOYMENT.md` - Render deployment notes.

## 3. Runtime Architecture

The application follows a simple three-part flow:

1. The agent starts, registers itself with the server, and receives an agent ID.
2. The agent periodically sends a beacon request to ask for queued tasks.
3. The server returns pending tasks, the agent executes them locally, then posts results back.
4. The client CLI can query agents, list tasks, queue commands, and fetch outputs.

The server uses SQLite as a local persistence store. This keeps setup simple, but it also means the current deployment model is not suitable for durable production storage without modification.

## 4. Main Components

### 4.1 Server

The server is implemented in `server/main.py` and uses FastAPI to expose REST endpoints. It initializes the database schema on startup and provides routes for:

- Registering agents.
- Polling for tasks via a beacon endpoint.
- Submitting task results.
- Listing agents.
- Creating and listing tasks.
- Fetching task results.

The server is backed by SQLAlchemy models defined in `server/models.py` and Pydantic request/response schemas defined in `server/schemas.py`.

### 4.2 Client CLI

The operator interface is implemented in `client/cli.py`. It uses `requests` to talk to the FastAPI server and exposes commands for:

- Listing active agents.
- Listing tasks for a specific agent.
- Queueing a command for an agent.
- Uploading and downloading files through task payloads.
- Retrieving a downloaded file once a result is available.

The CLI supports a configurable server URL through the `--url` option, which allows the same tool to work with a local server or a remotely deployed instance.

### 4.3 Agent

The agent is implemented in `agent/implant.py`. It is responsible for:

- Collecting host metadata such as hostname, IP address, and operating system.
- Registering with the server.
- Beaconing on a fixed interval with jitter.
- Executing tasks returned by the server.
- Posting execution output back to the server.

The agent currently supports a few built-in task types such as shell execution, `whoami`, sleep interval adjustment, upload, download, and a reverse-shell stub.

## 5. Data Model

The application uses three database entities.

### 5.1 Agent

Fields:

- `id`: UUID string primary key.
- `hostname`: Host name reported by the agent.
- `ip`: IP address reported by the agent.
- `os`: Platform string.
- `last_seen`: Last beacon time.
- `status`: Agent state, defaulting to `active`.

### 5.2 Task

Fields:

- `id`: Integer primary key.
- `agent_id`: Foreign key to `agents.id`.
- `command`: Task name.
- `arguments`: Optional task arguments.
- `status`: Task state, using `queued`, `sent`, or `completed`.
- `created_at`: Creation timestamp.

### 5.3 Result

Fields:

- `id`: Integer primary key.
- `task_id`: Foreign key to `tasks.id`.
- `output`: Task output or encoded file content.
- `executed_at`: Execution timestamp.

## 6. API Summary

### Server Health

- `GET /` - Returns a basic health response.

### Agent Lifecycle

- `POST /api/register` - Registers a new agent.
- `POST /api/beacon/{agent_id}` - Updates agent last-seen time and returns queued tasks.
- `POST /api/results` - Stores a task result and marks the task complete.

### Operator Functions

- `GET /api/agents` - Lists all registered agents.
- `POST /api/tasks/{agent_id}` - Creates a new task for an agent.
- `GET /api/tasks/{agent_id}` - Lists tasks for a given agent.
- `GET /api/results/{task_id}` - Retrieves a stored task result.

## 7. Client Commands

The operator CLI supports these commands:

- `agents` - List active agents.
- `tasks <agent_id>` - Show tasks for an agent.
- `tasks <agent_id> --show-output` - Show task outputs for completed tasks.
- `exec <agent_id> <command> [args]` - Queue a shell task.
- `upload <agent_id> <local_file> <remote_path>` - Queue a file write task.
- `download <agent_id> <remote_path> <local_file>` - Queue a file read task.
- `get-file <task_id> <local_file>` - Decode a completed download result into a local file.
- `get-id` - Print the first agent ID.
- `get-last-id` - Print the newest agent ID.

## 8. Agent Task Handling

The agent processes tasks sequentially. Each task is executed locally and its output is submitted back to the server.

Supported task names include:

- `shell` - Executes a shell command.
- `whoami` - Returns the local login name.
- `sleep` - Adjusts beacon interval.
- `upload` - Decodes base64 content and writes a file.
- `download` - Reads a local file and returns base64 content.
- `reverse_shell` - Attempts to spawn a reverse shell thread.

Task execution results are returned as plain output strings and stored in the results table.

## 9. Deployment Notes

The repository includes a Dockerfile and a Render configuration for running the server in a container.

Important operational detail:

- The current database uses SQLite at `sqlite:///./c2.db`.
- On ephemeral platforms, the database file is not durable unless a persistent volume or external database is configured.

## 10. Installation And Local Run

Suggested local workflow:

1. Create a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Start the server with Uvicorn.
4. Run the agent in a separate terminal.
5. Use the CLI to list agents and queue tasks.

Example commands:

```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn server.main:app --reload
python agent/implant.py
python client/cli.py agents
```

## 11. Operational Limitations

- SQLite is simple but not ideal for distributed or long-running deployments.
- The agent executes commands directly on the host, so its behavior must be controlled carefully.
- The current file transfer mechanism uses base64 inside task arguments and result payloads.
- The reverse shell capability is present in code and should be treated as high-risk functionality in any environment.

## 12. Recommended Improvements

- Replace SQLite with a production database for deployment persistence.
- Add authentication and authorization to the API.
- Add structured logging and task audit trails.
- Add tests for API routes, task execution, and CLI behavior.
- Split transport, task execution, and storage logic into smaller modules if the project grows.

## 13. Summary

This project is a compact C2-style research framework with a clear separation between server, operator, and agent responsibilities. Its structure is simple enough to understand quickly, but it already demonstrates registration, beaconing, queued task execution, and result collection.

*** Add File: E:\PROJECTS\C2\generate_project_report.py
"""Generate a detailed DOCX project report for the C2 repository.

The script collects a lightweight view of the repository structure and
produces a formatted Word document with sections that summarize the
project architecture, modules, APIs, data model, and usage.

Usage:
    python generate_project_report.py
    python generate_project_report.py --output my_report.docx
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = PROJECT_ROOT / "project_report.docx"


def collect_project_tree(root: Path) -> list[str]:
    """Return a small, readable tree of key project files."""

    interesting = []
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue

        relative = path.relative_to(root)
        parts = relative.parts
        if parts[0] in {"venv", ".git", "__pycache__"}:
            continue
        if path.suffix in {".pyc", ".db"}:
            continue

        if len(parts) == 1 or parts[0] in {"agent", "client", "server"}:
            interesting.append(str(relative).replace("\\", "/"))

    return interesting


def add_bullet(document: Document, text: str, level: int = 0) -> None:
    paragraph = document.add_paragraph(style="List Bullet")
    paragraph.paragraph_format.left_indent = Inches(0.25 * level)
    paragraph.add_run(text)


def add_code_block(document: Document, text: str) -> None:
    paragraph = document.add_paragraph()
    run = paragraph.add_run(text)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    paragraph.paragraph_format.space_after = Pt(6)


def add_section(document: Document, title: str, paragraphs: list[str], bullets: list[str] | None = None) -> None:
    document.add_heading(title, level=1)
    for paragraph_text in paragraphs:
        document.add_paragraph(paragraph_text)
    for bullet in bullets or []:
        add_bullet(document, bullet)


def build_document(output_path: Path) -> None:
    document = Document()

    title = document.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("C2 Framework Project Report")
    run.bold = True
    run.font.size = Pt(20)

    subtitle = document.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.add_run(f"Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")

    document.add_paragraph(
        "This report summarizes the repository structure, runtime design, API surface, data model, and usage patterns for the project."
    )

    add_section(
        document,
        "Executive Summary",
        [
            "The repository contains a small FastAPI-based C2-style framework split into server, client, and agent components.",
            "The server stores agents, tasks, and results in SQLite, while the client exposes operator commands and the agent performs beaconing and task execution.",
        ],
    )

    add_section(
        document,
        "Repository Structure",
        ["The project is organized around a minimal three-part architecture with a handful of supporting documentation files."],
        [
            "server/ - FastAPI server, models, schemas, and database configuration.",
            "client/ - Operator CLI for queueing tasks and inspecting agent state.",
            "agent/ - Polling implant that registers, receives tasks, and submits results.",
            "requirements.txt - Python dependencies used by the project.",
            "Dockerfile and render.yaml - Container and deployment configuration.",
        ],
    )

    add_section(
        document,
        "Runtime Flow",
        [
            "1. The agent registers with the server and receives a UUID identifier.",
            "2. The agent periodically beacons to ask for queued tasks.",
            "3. The server returns pending work and marks tasks as sent.",
            "4. The agent executes the task locally and posts the result back.",
            "5. The client CLI queries agents, lists tasks, and retrieves results.",
        ],
    )

    add_section(
        document,
        "Server API",
        [
            "The FastAPI application exposes endpoints for registration, beaconing, task creation, result submission, and operator listing queries.",
        ],
        [
            "GET / - health check.",
            "POST /api/register - create an agent record.",
            "POST /api/beacon/{agent_id} - fetch queued tasks and update last-seen time.",
            "POST /api/results - store task output and mark completion.",
            "GET /api/agents - list all agents.",
            "POST /api/tasks/{agent_id} - queue a task for an agent.",
            "GET /api/tasks/{agent_id} - list tasks for an agent.",
            "GET /api/results/{task_id} - fetch the stored result for a task.",
        ],
    )

    add_section(
        document,
        "Database Model",
        [
            "The project uses SQLAlchemy ORM models with an SQLite backend stored in c2.db.",
        ],
        [
            "Agent: hostname, ip, os, last_seen, status, and generated UUID primary key.",
            "Task: command, arguments, status, creation timestamp, and agent foreign key.",
            "Result: task output and execution timestamp linked to a task.",
        ],
    )

    add_section(
        document,
        "Operator CLI",
        [
            "The client CLI wraps the REST API and provides a simple workflow for managing agents and queued tasks.",
        ],
        [
            "agents - list active agents.",
            "tasks <agent_id> - list queued and completed tasks.",
            "exec <agent_id> <command> [args] - queue a shell execution task.",
            "upload <agent_id> <local_file> <remote_path> - queue a file write task.",
            "download <agent_id> <remote_path> <local_file> - queue a file read task.",
            "get-file <task_id> <local_file> - save a completed download result locally.",
        ],
    )

    add_section(
        document,
        "Agent Behavior",
        [
            "The agent implements a beacon loop with jitter and supports a small task vocabulary including shell execution, file transfer, and sleep adjustment.",
        ],
        [
            "Registers using host metadata gathered from socket and platform modules.",
            "Polls the beacon endpoint on a configurable interval.",
            "Executes tasks and posts results back to the server.",
            "Supports base64-encoded file transfer payloads.",
        ],
    )

    add_section(
        document,
        "Installation And Local Run",
        [
            "A typical local setup uses a Python virtual environment, installs dependencies, starts the FastAPI server, and then runs the agent and CLI in separate terminals.",
        ],
    )
    add_code_block(
        document,
        "python -m venv venv\nvenv\\Scripts\\activate\npip install -r requirements.txt\nuvicorn server.main:app --reload\npython agent/implant.py\npython client/cli.py agents",
    )

    add_section(
        document,
        "Deployment Notes",
        [
            "The repository includes Docker and Render configuration for containerized deployment.",
            "SQLite is convenient for local use but is not durable on ephemeral infrastructure without an external database or persistent disk.",
        ],
    )

    add_section(
        document,
        "Project Tree Snapshot",
        ["The following paths were collected automatically from the repository:"],
        collect_project_tree(PROJECT_ROOT),
    )

    add_section(
        document,
        "Recommended Improvements",
        [
            "The codebase would benefit from authentication, stronger persistence, structured logging, and test coverage for the API and CLI paths.",
        ],
        [
            "Replace SQLite with a production database for durable deployments.",
            "Add API authentication and authorization.",
            "Add tests for endpoints, task execution, and CLI flows.",
            "Split transport, persistence, and task execution into smaller modules as the project grows.",
        ],
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    document.save(output_path)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a DOCX project report for this repository.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Output DOCX file path")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    build_document(Path(args.output).resolve())
    print(f"Project report written to {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()