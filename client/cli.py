import requests
import sys
import json

SERVER_URL = "http://127.0.0.1:8000"

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

def main():
    if len(sys.argv) < 2:
        print("Usage: python cli.py <command> [args]")
        print("Commands:")
        print("  agents")
        print("  tasks <agent_id>")
        print("  exec <agent_id> <command> [args]")
        return

    cmd = sys.argv[1]
    
    if cmd == "agents":
        list_agents()
    elif cmd == "tasks":
        if len(sys.argv) < 3:
            print("Usage: python cli.py tasks <agent_id>")
            return
        list_tasks(sys.argv[2])
    elif cmd == "exec":
        if len(sys.argv) < 4:
            print("Usage: python cli.py exec <agent_id> <command> [args]")
            return
        agent_id = sys.argv[2]
        command = sys.argv[3]
        args = " ".join(sys.argv[4:]) if len(sys.argv) > 4 else None
        queue_task(agent_id, "shell", f"{command} {args}" if args else command)
    elif cmd == "get-id":
        try:
            response = requests.get(f"{SERVER_URL}/api/agents")
            agents = response.json()
            if agents:
                print(agents[0]['id'])
            else:
                print("No agents found")
        except Exception as e:
            print(f"[-] Error: {e}")
    elif cmd == "get-last-id":
        try:
            response = requests.get(f"{SERVER_URL}/api/agents")
            agents = response.json()
            if agents:
                print(agents[-1]['id'])
            else:
                print("No agents found")
        except Exception as e:
            print(f"[-] Error: {e}")
    elif cmd == "upload":
        if len(sys.argv) < 5:
            print("Usage: python cli.py upload <agent_id> <local_file> <remote_path>")
            return
        agent_id = sys.argv[2]
        local_file = sys.argv[3]
        remote_path = sys.argv[4]
        try:
            import base64
            with open(local_file, "rb") as f:
                content = base64.b64encode(f.read()).decode()
            queue_task(agent_id, "upload", f"{remote_path} {content}")
        except Exception as e:
            print(f"[-] Error reading file: {e}")
    elif cmd == "download":
        if len(sys.argv) < 5:
            print("Usage: python cli.py download <agent_id> <remote_path> <local_file>")
            return
        agent_id = sys.argv[2]
        remote_path = sys.argv[3]
        local_file = sys.argv[4]
        queue_task(agent_id, "download", remote_path)
        print(f"[*] Queued download task. Run 'python cli.py tasks {agent_id}' to check status.")
        # Note: Actual file saving would happen when parsing results, which requires updating list_tasks or adding a new command to fetch result and save.
        # For now, let's update list_tasks to handle saving if a flag is passed or just print it.
        # Actually, let's add a `get-file` command to fetch result and save.
    elif cmd == "get-file":
        if len(sys.argv) < 4:
            print("Usage: python cli.py get-file <task_id> <local_file>")
            return
        task_id = sys.argv[2]
        local_file = sys.argv[3]
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
    else:
        print("Unknown command")

if __name__ == "__main__":
    main()
