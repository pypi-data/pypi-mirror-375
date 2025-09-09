import socket
import subprocess
import time


def find_available_port(preferred_ports=[4444, 4445, 4446, 4447]):
    """Find an available port from the preferred list"""
    for port in preferred_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    
    # If none of the preferred ports work, find any available port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 0))
        return s.getsockname()[1]


def kill_process_on_port(port, debug=False):
    """Kill any existing process using the specified port"""
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        if result.stdout.strip():
            existing_pids = result.stdout.strip().split('\n')
            for pid in existing_pids:
                if pid:
                    if debug:
                        print(f"   🔄 Stopping existing process on port {port} (PID: {pid})")
                    subprocess.run(['kill', '-9', pid], capture_output=True)
            time.sleep(1)  # Wait for the port to be freed
            return True
    except:
        pass
    return False


def check_docker_available():
    """Check if Docker is available on the system"""
    try:
        subprocess.run(["docker", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_container_running(container_name):
    """Check if a Docker container is running"""
    try:
        check_cmd = ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Status}}"]
        result = subprocess.run(check_cmd, capture_output=True, text=True)
        return result.returncode == 0 and "Up" in result.stdout
    except:
        return False


def stop_docker_container(container_name, debug=False):
    """Stop and remove a Docker container"""
    try:
        # Stop existing container if running
        subprocess.run(["docker", "stop", container_name], 
                     capture_output=True, check=False)
        subprocess.run(["docker", "rm", container_name], 
                     capture_output=True, check=False)
        
        if debug:
            print(f"   🛑 Stopped container: {container_name}")
        return True
    except:
        return False
