import os
import subprocess
import time
from .utils import check_docker_available, check_container_running, stop_docker_container


class DockerManager:
    """Manages Docker operations for NovaTrace web interface"""
    
    def __init__(self, debug=False):
        self.debug = debug
    
    def build_image_if_needed(self, web_interface_dir, image_name, container_name, force_rebuild=False):
        """Build Docker image if it doesn't exist or if force rebuild is requested"""
        
        if not check_docker_available():
            print("❌ Docker not found. Please install Docker to use the web interface.")
            return False
        
        # Clean up old duplicate images
        self._cleanup_old_images()
        
        # Stop existing container if running
        stop_docker_container(container_name, self.debug)
        
        # Check if image already exists
        image_check = subprocess.run(
            ["docker", "images", "-q", image_name], 
            capture_output=True, text=True
        )
        image_exists = bool(image_check.stdout.strip())
        
        # Check if we need to rebuild
        if not force_rebuild and image_exists:
            # Check if entrypoint script exists in the image
            inspect_result = subprocess.run([
                "docker", "run", "--rm", "--entrypoint", "ls", image_name, "/docker-entrypoint.sh"
            ], capture_output=True, text=True)
            if inspect_result.returncode != 0:
                if self.debug:
                    print("   🔄 Detected old Docker image without dynamic port detection")
                force_rebuild = True
        
        # Build if needed
        if not image_exists or force_rebuild:
            return self._build_image(web_interface_dir, image_name, force_rebuild)
        
        if self.debug:
            print("   ✅ Using existing Docker image with dynamic port detection")
        return True
    
    def _cleanup_old_images(self):
        """Clean up old duplicate images"""
        try:
            subprocess.run([
                "docker", "rmi", 
                "nova-web:latest", 
                "novatrace-web:latest", 
                "novatrace-novatrace-web:latest"
            ], capture_output=True, check=False)
        except:
            pass
    
    def _build_image(self, web_interface_dir, image_name, force_rebuild):
        """Build the Docker image"""
        build_cmd = ["docker", "build", "-t", image_name, "."]
        
        if force_rebuild and self.debug:
            print("   🔄 Force rebuilding Docker image...")
        elif self.debug:
            print("   🔨 Building Docker image...")
        
        if self.debug:
            print("   ✅ Docker build logs will be shown below:")
            print("   " + "="*50)
            build_process = subprocess.Popen(build_cmd, cwd=web_interface_dir)
        else:
            build_process = subprocess.Popen(
                build_cmd, 
                cwd=web_interface_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        build_process.wait()
        
        if build_process.returncode != 0:
            print("   ❌ Docker build failed")
            return False
        
        # Check what images were actually created
        list_images_cmd = [
            "docker", "images", 
            "--format", "{{.Repository}}:{{.Tag}}", 
            "--filter", "reference=*novatrace*"
        ]
        images_result = subprocess.run(list_images_cmd, capture_output=True, text=True)
        print(f"🏷️  Images created: {images_result.stdout.strip()}")
        
        if self.debug:
            print("   ✅ Docker image built successfully with dynamic port detection")
        
        return True
    
    def run_container(self, container_name, image_name, web_interface_dir):
        """Run the Docker container"""
        run_cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "-p", "3000:80",
            "--add-host", "host.docker.internal:host-gateway",
            image_name
        ]
        
        if self.debug:
            docker_process = subprocess.Popen(run_cmd, cwd=web_interface_dir)
        else:
            docker_process = subprocess.Popen(
                run_cmd, 
                cwd=web_interface_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        docker_process.wait()
        
        # Wait a bit for the container to start
        time.sleep(3)
        
        # Check if container is running
        if check_container_running(container_name):
            print("   ✅ Dashboard disponible en: http://localhost:3000")
            if self.debug:
                print("   📊 Dashboard: http://localhost:3000/")
                print("   📁 Projects: http://localhost:3000/projects")
                print("   ⚙️  Settings: http://localhost:3000/settings")
                print("   💡 Use debug=False to hide detailed logs")
            return docker_process
        else:
            print("   ❌ Error starting Docker container")
            return None
