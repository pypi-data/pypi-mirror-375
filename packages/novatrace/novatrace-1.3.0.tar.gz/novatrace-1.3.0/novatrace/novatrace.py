import json
import functools
from .database.model import Session, Project, Trace, Base, engine as default_engine, sessionmaker, TraceTypes
from sqlalchemy import create_engine, inspect, text
from datetime import datetime
from .connect import hora
from typing import Dict, Union
import pytz
import inspect as py_inspect
import threading
import subprocess
import os

# Import web interface registry from backend
from .backend.registry import get_registry, increment_instance_count
from .backend.utils import find_available_port, kill_process_on_port
from .backend.docker_manager import DockerManager

class NovaTracer:
    """Individual tracer instance for tracking specific workflows"""
    def __init__(self, parent_instance: 'NovaTrace'):
        self._parent = parent_instance
        self.session = parent_instance.session
        self.engine = parent_instance.engine
        self.time_zone = parent_instance.time_zone
        self.debug = parent_instance.debug
        
        # Use the same session as the parent NovaTrace instance
        self.active_session = parent_instance.active_session
        
        # Generate a unique identifier for this tracer (for internal tracking)
        import time
        import random
        self._tracer_id = f"tracer_{int(time.time() * 1000)}_{random.randint(100, 999)}"
        
        # Tracer-specific state
        self.project = None
        self.provider: str = None
        self.model: str = None
        self.input_cost_per_million_tokens: float = 0.0
        self.output_cost_per_million_tokens: float = 0.0
        self.user_external_id: str = "guest_user"
        self.user_external_name: str = "Guest User"
        
        if self.debug:
            print(f"✨ Created tracer: {self._tracer_id} (using session: {self.active_session.name})")

    def _get_trace_type_id(self, type_name: str) -> int:
        """Get trace type ID from parent instance"""
        return self._parent._get_trace_type_id(type_name)

    def _log_trace(self, type_id: int, input_data, output_data, request_time, response_time,
                   input_tokens=0, output_tokens=0, model_name=None, model_provider=None,
                   user_external_id=None, user_external_name=None):
        """Log trace using this tracer's specific session and project"""
        try:
            if not self.session or not self.project or not self.active_session:
                print("Warning: Tracer not properly initialized, cannot log trace")
                return
                
            duration = (response_time - request_time).total_seconds() * 1000  # ms
            trace = Trace(
                type_id=type_id,
                input_data=json.dumps(input_data, default=str),
                output_data=json.dumps(output_data, default=str),
                project_id=self.project.id,
                session_id=self.active_session.id,  # Use this tracer's session
                created_at=response_time,
                request_time=request_time,
                response_time=response_time,
                duration_ms=duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                model_provider=model_provider if model_provider else self.provider,
                model_name=model_name if model_name else self.model,
                model_input_cost=self.input_cost_per_million_tokens,
                model_output_cost=self.output_cost_per_million_tokens,
                call_cost = ((input_tokens * (self.input_cost_per_million_tokens/1000000)) + (output_tokens * (self.output_cost_per_million_tokens/1000000))),
                user_external_id=user_external_id,
                user_external_name=user_external_name
            )
            self.session.add(trace)
            self.session.commit()
        except Exception as e:
            print(f"Warning: Tracer _log_trace failed: {e}")

    def _get_named_args(self, func, *args, **kwargs):
        """Get named arguments using parent instance method"""
        return self._parent._get_named_args(func, *args, **kwargs)

    def _extract_user_info(self, func, *args, **kwargs):
        """Extract user info using parent instance method"""
        return self._parent._extract_user_info(func, *args, **kwargs)

    def tokenizer(self, response) -> Dict[str, Union[int, float]]:
        """
        Count tokens in a response string.
        Args:
            response: The response string to count tokens for.
        Returns:
            Dict containing input_tokens and output_tokens counts.
        """
        return self._parent.tokenizer(response)

    def metadata(self, metadata: Dict[str, Union[str, float]]):
        """
        Set metadata for the tracer including model information and costs.
        Args:
            metadata (Dict): Dictionary containing model metadata.
        """
        if "provider" in metadata:
            self.provider = metadata["provider"]
        if "model" in metadata:
            self.model = metadata["model"]
        if "input_cost_per_million_tokens" in metadata:
            self.input_cost_per_million_tokens = metadata["input_cost_per_million_tokens"]
        if "output_cost_per_million_tokens" in metadata:
            self.output_cost_per_million_tokens = metadata["output_cost_per_million_tokens"]

    def set_user(self, user_id: str = None, user_name: str = None):
        """
        Set user information for this tracer.
        Args:
            user_id (str): External user ID.
            user_name (str): External user name.
        """
        if user_id is not None:
            self.user_external_id = user_id
        if user_name is not None:
            self.user_external_name = user_name

    def create_project(self, project_name: str):
        """
        Create a new project and associate this tracer's session with it.
        If the project already exists, connects to it instead.
        Args:
            project_name (str): Name of the project to be created.
        """
        try:
            if not self.session or not self.active_session:
                print("Warning: Tracer not properly initialized, cannot create project")
                return
            
            # First try to connect to existing project (silently)
            existing_project = self.connect_to_project(project_name, silent=True)
            if existing_project:
                # Project exists and we're now connected to it
                if self.debug:
                    print(f"🔗 Connected to existing project '{project_name}'")
                return existing_project
            
            # Project doesn't exist, create a new one
            self.project = Project(
                name=project_name, 
                created_at=datetime.now(self.time_zone),
                updated_at=datetime.now(self.time_zone)
            )
            self.session.add(self.project)
            self.session.commit()
            
            # Associate current session with the new project
            self.active_session.project_id = self.project.id
            self.session.commit()
            
            if self.debug:
                print(f"✨ Created new project '{project_name}' and connected tracer session")
            
            return self.project
            
        except Exception as e:
            print(f"Warning: Tracer create_project failed: {e}")
            return None

    def connect_to_project(self, project_name: str, silent: bool = False):
        """
        Connect to an existing project and associate this tracer's session with it.
        If the project doesn't exist, creates it automatically.
        Args:
            project_name (str): Name of the project to connect to.
            silent (bool): If True, suppress messages.
        Returns:
            Project: The project object.
        """
        try:
            if not self.session or not self.active_session:
                if not silent:
                    print("Warning: Tracer not properly initialized, cannot connect to project")
                return None
                
            # Buscar proyecto globalmente
            self.project = self.session.query(Project).filter_by(name=project_name).first()
            if not self.project:
                # Project doesn't exist, create it
                self.project = Project(
                    name=project_name, 
                    created_at=datetime.now(self.time_zone),
                    updated_at=datetime.now(self.time_zone)
                )
                self.session.add(self.project)
                self.session.commit()
                
                if not silent and self.debug:
                    print(f"✨ Created new project '{project_name}' (via connect_to_project)")
                
            # Asociar la sesión actual al proyecto
            self.active_session.project_id = self.project.id
            self.session.commit()
            
            if not silent:
                print(f"Tracer connected to project '{project_name}' with session '{self.active_session.name}'")
            return self.project
        except Exception as e:
            if not silent:
                print(f"Warning: Tracer connect_to_project failed: {e}")
            return None

    def llm(self, func):
        """
        Decorator for LLM functions to log traces.
        Args:
            func: The function to be decorated.
        Returns:
            The decorated function.
        """
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                request_time = datetime.now(self.time_zone)
                
                # Extract user information before function call
                user_id, user_name = self._extract_user_info(func, *args, **kwargs)
                
                result = func(*args, **kwargs)
                tokens = self.tokenizer(result)
                response_time = datetime.now(self.time_zone)
                
                # Obtener argumentos con la nueva lógica mejorada
                _args = self._get_named_args(func, *args, **kwargs)
                
                self._log_trace(self._get_trace_type_id("LLM"), {"args": _args}, 
                                result, request_time, response_time,
                                tokens.get("input_tokens", 0),
                                tokens.get("output_tokens", 0),
                                model_name=kwargs.get("model_name", self.model),
                                model_provider=kwargs.get("model_provider", self.provider),
                                user_external_id=user_id,
                                user_external_name=user_name
                                )
                
                return result
            except Exception as e:
                print(f"Warning: Tracer LLM decorator failed: {e}")
                return func(*args, **kwargs)
        return wrapper

    def agent(self, func):
        """
        Decorator for Agent functions to log traces.
        Args:
            func: The function to be decorated.
        Returns:
            The decorated function.
        """
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                request_time = datetime.now(self.time_zone)
                
                # Extract user information before function call
                user_id, user_name = self._extract_user_info(func, *args, **kwargs)
                
                result = func(*args, **kwargs)
                tokens = self.tokenizer(result)
                response_time = datetime.now(self.time_zone)
                
                # Obtener argumentos con la nueva lógica mejorada
                _args = self._get_named_args(func, *args, **kwargs)
                
                self._log_trace(self._get_trace_type_id("Agent"), {"args": _args}, 
                                result, request_time, response_time,
                                tokens.get("input_tokens", 0),
                                tokens.get("output_tokens", 0),
                                model_name=kwargs.get("model_name", self.model),
                                model_provider=kwargs.get("model_provider", self.provider),
                                user_external_id=user_id,
                                user_external_name=user_name
                                )
                
                return result
            except Exception as e:
                print(f"Warning: Tracer Agent decorator failed: {e}")
                return func(*args, **kwargs)
        return wrapper

    def tool(self, func):
        """
        Decorator for Tool functions to log traces.
        Args:
            func: The function to be decorated.
        Returns:
            The decorated function.
        """
        import functools
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                request_time = datetime.now(self.time_zone)
                
                # Extract user information before function call
                user_id, user_name = self._extract_user_info(func, *args, **kwargs)
                
                result = func(*args, **kwargs)
                response_time = datetime.now(self.time_zone)
                
                # Obtener argumentos con la nueva lógica mejorada
                _args = self._get_named_args(func, *args, **kwargs)
                
                # Tools don't typically use tokenization
                self._log_trace(self._get_trace_type_id("Tool"), {"args": _args}, 
                                result, request_time, response_time,
                                0, 0,  # No tokens for tools
                                model_name=kwargs.get("model_name", self.model),
                                model_provider=kwargs.get("model_provider", self.provider),
                                user_external_id=user_id,
                                user_external_name=user_name
                                )
                
                return result
            except Exception as e:
                print(f"Warning: Tracer Tool decorator failed: {e}")
                return func(*args, **kwargs)
        return wrapper

    def close(self):
        """
        Close this tracer (no-op since tracers share the parent's session).
        The parent NovaTrace instance manages the database connection.
        """
        if self.debug:
            print(f"📝 Tracer '{self._tracer_id}' closed (session remains active in parent)")

class NovaTrace:
    _instance = None
    _initialized = False
    
    def __new__(cls, session_name: str = "default", engine_url: str = None, time_zone: pytz.tzinfo = pytz.utc, interface: bool = True, debug: bool = False):
        if cls._instance is None:
            cls._instance = super(NovaTrace, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, session_name: str = "default", engine_url: str = None, time_zone: pytz.tzinfo = pytz.utc, interface: bool = True, debug: bool = False):
        """
        Init a new NovaTrace instance (singleton pattern).
        Args:
            session_name (str): Name of the session to be created or connected to.
            engine_url (str, optional): SQLAlchemy engine URL. If not provided, defaults to the default engine.
            time_zone (pytz.tzinfo, optional): Time zone for timestamps. Defaults to UTC.
            interface (bool, optional): Whether to start the web interface. Defaults to True.
            debug (bool, optional): Whether to show detailed logs. Defaults to False.
        Raises:
            ValueError: If metadata is not provided or incomplete.
        Returns:
            None
        """
        # Prevent re-initialization of singleton
        if self.__class__._initialized:
            return
            
        registry = get_registry()
        
        try:
            # Original NovaTrace attributes
            self.time_zone = time_zone
            self.interface_enabled = interface
            self.debug = debug
            self.reflex_process = None
            
            # Track this instance
            self._instance_id = increment_instance_count()
            
            # Only set up web interface resources for the first interface-enabled instance
            if interface and not registry['interface_enabled']:
                registry['interface_enabled'] = True
                self._is_interface_owner = True
            else:
                self._is_interface_owner = False
            
            if engine_url:
                # Crear engine con configuraciones para manejo de reconexión
                self.engine = create_engine(
                    engine_url,
                    pool_pre_ping=True,  # Verificar conexión antes de usar
                    pool_recycle=3600,   # Reciclar conexiones cada hora
                    connect_args={'connect_timeout': 10} if 'mysql' in engine_url else {}
                )
            else:
                self.engine = default_engine
            
            # Almacenar el engine en el registro global para que la API lo pueda usar
            if self._is_interface_owner:
                registry['engine'] = self.engine
            
            # Handle database migration for session_id column
            self._migrate_database_if_needed()
            
            Base.metadata.create_all(self.engine)
            session = sessionmaker(bind=self.engine)

            self.session = session() # Sesion de SQLAlchemy

            for name in ["LLM", "Agent", "Tool"]:
                if not self.session.query(TraceTypes).filter_by(name=name).first():
                    new_type = TraceTypes(name=name)
                    self.session.add(new_type) 
            self.session.commit() # BDD Build

            self.active_session = self.session.query(Session).filter_by(name=session_name).first()

            if not self.active_session:
                self.active_session = Session(name=session_name, created_at=datetime.now(self.time_zone))
                self.session.add(self.active_session)
                self.session.commit()
            self.project = None
            self.provider: str = None
            self.model: str = None
            self.input_cost_per_million_tokens: float = 0.0
            self.output_cost_per_million_tokens: float = 0.0
            self.user_external_id: str = "guest_user"
            self.user_external_name: str = "Guest User"
            
            # Register cleanup only for database session (not web interface)
            self._register_cleanup_handlers()
            
            # Initialize database with correct engine if this instance owns the interface
            if self._is_interface_owner:
                from .database.init_db import init_database
                init_database(self.engine)
            
            # Start interface if this instance owns it
            if self._is_interface_owner:
                self._start_web_interface()
            
            # Mark as initialized
            self.__class__._initialized = True
                
        except Exception as e:
            print(f"Warning: NovaTrace initialization failed: {e}")
            # Initialize with minimal safe defaults
            self.session = None
            self.project = None
            self.provider = None
            self.model = None
            self.input_cost_per_million_tokens = 0.0
            self.output_cost_per_million_tokens = 0.0
            self.user_external_id = "guest_user"
            self.user_external_name = "Guest User"
            self.interface_enabled = False
            self.debug = False
            self.reflex_process = None
            self._is_interface_owner = False

    def create_tracer(self) -> 'NovaTracer':
        """
        Create a new independent tracer instance that shares the same session.
        
        Returns:
            NovaTracer: A new tracer instance that uses the same session as this NovaTrace
        """
        tracer = NovaTracer(self)
        
        if self.debug:
            print(f"📍 Created new tracer using session: {self.active_session.name}")
            
        return tracer
    
    def _register_cleanup_handlers(self):
        """Register cleanup handlers only for database session"""
        import atexit
        
        # Only register cleanup for database session - NO automatic interface cleanup
        atexit.register(self._cleanup_session)
    
    def _cleanup_session(self):
        """Clean up only the database session"""
        try:
            if hasattr(self, 'session') and self.session:
                self.session.close()
        except Exception:
            pass  # Ignore errors in cleanup
    
    def _handle_db_error(self, error_context="database operation"):
        """Handle database errors with proper rollback and session refresh"""
        try:
            if hasattr(self, 'session') and self.session:
                # Rollback any pending transaction
                self.session.rollback()
                # Close the current session
                self.session.close()
                # Create a new session
                SessionLocal = sessionmaker(bind=self.engine)
                self.session = SessionLocal()
                if self.debug:
                    print(f"NovaTrace: Database session refreshed after error in {error_context}")
        except Exception as e:
            if self.debug:
                print(f"NovaTrace: Failed to refresh session after error: {e}")
    
    def _migrate_database_if_needed(self):
        """Handle database migration for new structure"""
        try:
            inspector = inspect(self.engine)
            
            # Check if session_id column exists in traces table
            if 'traces' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('traces')]
                if 'session_id' not in columns:
                    # Add session_id column to existing traces table
                    with self.engine.connect() as conn:
                        conn.execute(text("ALTER TABLE traces ADD COLUMN session_id INTEGER"))
                        conn.commit()
                        print("NovaTrace: Added session_id column to traces table")
            
            # Handle migration from old structure to new structure
            if 'projects' in inspector.get_table_names() and 'sessions' in inspector.get_table_names():
                project_columns = [col['name'] for col in inspector.get_columns('projects')]
                session_columns = [col['name'] for col in inspector.get_columns('sessions')]
                
                # If projects still have session_id, we need to migrate
                if 'session_id' in project_columns and 'project_id' not in session_columns:
                    print("NovaTrace: Migrating database structure - Projects now own Sessions")
                    
                    with self.engine.connect() as conn:
                        # Add project_id column to sessions
                        conn.execute(text("ALTER TABLE sessions ADD COLUMN project_id INTEGER"))
                        
                        # Add description and updated_at to projects
                        conn.execute(text("ALTER TABLE projects ADD COLUMN description VARCHAR(500)"))
                        conn.execute(text("ALTER TABLE projects ADD COLUMN updated_at DATETIME"))
                        
                        # Make project names unique
                        conn.execute(text("ALTER TABLE projects ADD CONSTRAINT unique_project_name UNIQUE (name)"))
                        
                        conn.commit()
                        print("NovaTrace: Database migration completed")
                        
        except Exception as e:
            if self.debug:
                print(f"NovaTrace: Database migration warning: {e}")
            pass  # Continue if migration fails
        except Exception as e:
            print(f"Warning: NovaTrace database migration failed: {e}")
    
    def _start_web_interface(self):
        """
        Start the web interface. Tries React interface first, falls back to Reflex.
        """
        registry = get_registry()
        
        # Only start if we're the interface owner
        if not self._is_interface_owner:
            return
        
        # Prevent multiple starts
        if registry['interface_started']:
            if self.debug:
                print("   💡 Web interface already started")
            return
        
        registry['interface_started'] = True
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        react_interface_dir = os.path.join(current_dir, "web_interface")
        
        # Store reference in global registry
        registry['reflex_process'] = None
        
        # Check if new React interface exists
        if os.path.exists(react_interface_dir):
            self._start_react_interface()
        else:
            # Fallback to original Reflex interface
            self._start_reflex_interface()
    
    def _start_react_interface(self):
        """
        Start the React web interface using Docker.
        This will start the containerized React app on port 3000.
        """
        registry = get_registry()
        
        def run_web_interface():
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
                web_interface_dir = os.path.join(current_dir, "web_interface")
                
                # Start API server first
                self._start_api_server()
                
                # Check if Docker is available
                try:
                    subprocess.run(["docker", "--version"], capture_output=True, check=True)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("❌ Docker not found. Please install Docker to use the web interface.")
                    return
                
                # Build Docker image if it doesn't exist
                container_name = registry['container_name']
                image_name = "novatrace-webapp:latest"
                build_cmd = ["docker", "build", "-t", image_name, "."]
                
                print("🚀 Iniciando NovaTrace con dashboard...")
                print(f"🐳 Container name: {container_name}")
                print(f"🏷️  Image name: {image_name}")
                print(f"🔨 Build command: {' '.join(build_cmd)}")
                
                # Clean up old duplicate images
                try:
                    subprocess.run(["docker", "rmi", "nova-web:latest", "novatrace-web:latest", "novatrace-novatrace-web:latest"], 
                                 capture_output=True, check=False)
                except:
                    pass
                
                # Stop existing container if running
                try:
                    subprocess.run(["docker", "stop", container_name], 
                                 capture_output=True, check=False)
                    subprocess.run(["docker", "rm", container_name], 
                                 capture_output=True, check=False)
                except:
                    pass
                
                # Check if image already exists and if we need to rebuild
                image_check = subprocess.run(
                    ["docker", "images", "-q", image_name], 
                    capture_output=True, text=True
                )
                image_exists = bool(image_check.stdout.strip())
                
                # Check if we need to rebuild (dockerfile or entrypoint changed)
                force_rebuild = getattr(self, 'force_rebuild', False)
                if not force_rebuild and image_exists:
                    # Check if entrypoint script exists in the image (simple way to detect old image)
                    inspect_result = subprocess.run([
                        "docker", "run", "--rm", "--entrypoint", "ls", image_name, "/docker-entrypoint.sh"
                    ], capture_output=True, text=True)
                    if inspect_result.returncode != 0:
                        if self.debug:
                            print("   🔄 Detected old Docker image without dynamic port detection")
                        force_rebuild = True
                
                if not image_exists or force_rebuild:
                    if force_rebuild and self.debug:
                        print("   Rebuilding Docker image (with dynamic port detection)...")
                    elif self.debug:
                        print("   Building Docker image (first time)...")
                    
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
                        return
                    
                    # Check what images were actually created
                    list_images_cmd = ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}", "--filter", "reference=*novatrace*"]
                    images_result = subprocess.run(list_images_cmd, capture_output=True, text=True)
                    print(f"🏷️  Images created: {images_result.stdout.strip()}")
                    
                    if self.debug:
                        print("   ✅ Docker image built successfully with dynamic port detection")
                elif self.debug:
                    print("   ✅ Using existing Docker image with dynamic port detection")
                    print("   💡 Image will automatically detect API port at startup")
                
                # Run the Docker container
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
                
                # Store in global registry
                registry['reflex_process'] = docker_process
                
                # Wait a bit for the container to start
                import time
                time.sleep(3)
                
                # Check if container is running
                check_cmd = ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Status}}"]
                result = subprocess.run(check_cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and "Up" in result.stdout:
                    print("   Web interface running at: http://localhost:3000/")
                    if self.debug:
                        print("   📊 Dashboard: http://localhost:3000/")
                        print("   📁 Projects: http://localhost:3000/projects")
                        print("   ⚙️  Settings: http://localhost:3000/settings")
                        print("   💡 Use debug=False to hide detailed logs")
                else:
                    print("   ❌ Container failed to start")
                        
            except Exception as e:
                print(f"Warning: Could not start React web interface: {e}")
                # Fallback to old Reflex interface
                print("   Falling back to legacy Reflex interface...")
                self._start_reflex_interface()
        
        # Start web interface in a separate thread so it doesn't block the main application
        web_thread = threading.Thread(target=run_web_interface, daemon=True)
        web_thread.start()
    
    def _start_reflex_interface(self):
        """
        Start the Reflex web interface in a separate thread.
        This will start both frontend (port 3000) and backend (port 8000).
        """
        def run_reflex():
            try:
                # Change to the web_interface directory where rxconfig.py is located
                current_dir = os.path.dirname(os.path.abspath(__file__))
                web_interface_dir = os.path.join(current_dir, "web_interface_old")
                novatrace_root = os.path.dirname(current_dir)  # Parent directory of novatrace package
                
                # Check if web_interface directory exists
                if not os.path.exists(web_interface_dir):
                    print("❌ Web interface directory not found. Creating basic structure...")
                    return
                
                # Set up environment with correct PYTHONPATH
                env = os.environ.copy()
                env['PYTHONPATH'] = f"{novatrace_root}:{env.get('PYTHONPATH', '')}"
                    
                # Run reflex run command with proper flags
                if self.interface_logs:
                    # Show all logs when interface_logs=True
                    print("🚀 NovaTrace interface starting...")
                    print("   Frontend: http://localhost:3000")
                    print("   Backend:  http://localhost:8000")
                    print("   ✅ All Reflex logs will be shown below:")
                    print("   " + "="*50)
                    
                    # Use no redirection to show all logs
                    self.reflex_process = subprocess.Popen(
                        ["reflex", "run", "--env", "dev", "--loglevel", "debug"],
                        cwd=web_interface_dir,
                        env=env
                    )
                else:
                    # Hide logs when interface_logs=False (default)
                    DEVNULL = subprocess.DEVNULL
                    self.reflex_process = subprocess.Popen(
                        ["reflex", "run", "--env", "dev"],
                        cwd=web_interface_dir,
                        env=env,
                        stdout=DEVNULL,  # Hide stdout logs
                        stderr=DEVNULL,  # Hide stderr logs
                        text=True
                    )
                    print("🚀 NovaTrace interface starting...")
                    print("   Frontend: http://localhost:3000")
                    print("   Backend:  http://localhost:8000")
                
                # Wait a bit for the process to start
                import time
                time.sleep(2)
                
                if self.reflex_process.poll() is None:
                    print("   ✅ App running at: http://localhost:3000/")
                    if not self.interface_logs:
                        print("   💡 Use interface_logs=True to see detailed logs")
                else:
                    print("   ❌ Process failed to start")
                        
            except Exception as e:
                print(f"Warning: Could not start Reflex interface: {e}")
        
        # Start Reflex in a separate thread so it doesn't block the main application
        reflex_thread = threading.Thread(target=run_reflex, daemon=True)
        reflex_thread.start()
    
    def _find_available_port(self, preferred_ports=[4444, 4445, 4446, 4447]):
        """Find an available port from the preferred list"""
        return find_available_port(preferred_ports)

    def _kill_process_on_port(self, port):
        """Kill any existing process using the specified port"""
        return kill_process_on_port(port, self.debug)
        return False

    def _start_api_server(self):
        """
        Start the FastAPI server for the web interface.
        This will start the API server on port 4444 or next available port.
        """
        registry = get_registry()
        
        def run_api_server():
            try:
                # Find available port
                api_port = self._find_available_port()
                registry['api_port'] = api_port
                
                if self.debug:
                    print("🔌 Starting NovaTrace API server...")
                    print(f"   API will be available at: http://localhost:{api_port}")
                    
                    if api_port != 4444:
                        print(f"   💡 Using port {api_port} (4444 was occupied)")
                
                # Import and start FastAPI
                import uvicorn
                from .api.api import app
                
                # Configure uvicorn to run quietly unless debug=True
                if self.debug:
                    log_level = "info"
                    print("   ✅ API logs will be shown below:")
                    print("   " + "="*50)
                else:
                    log_level = "error"  # Only show errors
                
                # Start the API server
                uvicorn.run(
                    app, 
                    host="0.0.0.0", 
                    port=api_port,
                    log_level=log_level,
                    access_log=self.debug
                )
                
            except Exception as e:
                print(f"Warning: Could not start API server: {e}")
        
        # Start API server in a separate thread
        api_thread = threading.Thread(target=run_api_server, daemon=True)
        registry['api_thread'] = api_thread
        api_thread.start()
        
        # Give the API server a moment to start
        import time
        time.sleep(2)
    
    def _start_reflex_interface(self):
        """
        Start the legacy Reflex web interface (fallback).
        This will start both frontend (port 3000) and backend (port 8000).
        """
        def run_reflex():
            try:
                # Change to the web_interface_old directory where rxconfig.py is located
                current_dir = os.path.dirname(os.path.abspath(__file__))
                web_interface_dir = os.path.join(current_dir, "web_interface_old")
                novatrace_root = os.path.dirname(current_dir)  # Parent directory of novatrace package
                
                # Check if web_interface_old directory exists
                if not os.path.exists(web_interface_dir):
                    print("❌ Legacy web interface directory not found.")
                    return
                
                # Set up environment with correct PYTHONPATH
                env = os.environ.copy()
                env['PYTHONPATH'] = f"{novatrace_root}:{env.get('PYTHONPATH', '')}"
                    
                # Run reflex run command with proper flags
                if self.debug:
                    # Show all logs when debug=True
                    print("🚀 NovaTrace legacy interface starting...")
                    print("   Frontend: http://localhost:3000")
                    print("   Backend:  http://localhost:8000")
                    print("   ✅ All Reflex logs will be shown below:")
                    print("   " + "="*50)
                    
                    # Use no redirection to show all logs
                    self.reflex_process = subprocess.Popen(
                        ["reflex", "run", "--env", "dev", "--loglevel", "debug"],
                        cwd=web_interface_dir,
                        env=env
                    )
                else:
                    # Hide logs when debug=False (default)
                    DEVNULL = subprocess.DEVNULL
                    self.reflex_process = subprocess.Popen(
                        ["reflex", "run", "--env", "dev"],
                        cwd=web_interface_dir,
                        env=env,
                        stdout=DEVNULL,  # Hide stdout logs
                        stderr=DEVNULL,  # Hide stderr logs
                        text=True
                    )
                    print("🚀 NovaTrace legacy interface starting...")
                    print("   Frontend: http://localhost:3000")
                    print("   Backend:  http://localhost:8000")
                
                # Wait a bit for the process to start
                import time
                time.sleep(2)
                
                if self.reflex_process.poll() is None:
                    print("   ✅ App running at: http://localhost:3000/")
                    if not self.debug:
                        print("   💡 Use debug=True to see detailed logs")
                else:
                    print("   ❌ Process failed to start")
                        
            except Exception as e:
                print(f"Warning: Could not start Reflex interface: {e}")
        
        # Start Reflex in a separate thread so it doesn't block the main application
        reflex_thread = threading.Thread(target=run_reflex, daemon=True)
        reflex_thread.start()
        
    def close(self):
        """
        Close the current session and connection to the database.
        Also stops the web interface if it's running.
        Returns:
            None
        """
        try:
            # Force cleanup when explicitly calling close()
            self.cleanup(force=True)
                    
        except Exception as e:
            print(f"Warning: NovaTrace close failed: {e}")

    def list_projects(self):
        """
        List all projects (globally).
        """
        return self.session.query(Project).all()
    
    def tokenizer(self, response) -> Dict[str, Union[int, float]]:
        """
        Tokenizer to calculate the number of tokens used in a response and their cost.
        Args:
            response: The response object from the LLM or agent.
        Returns:
            Dict[str, Union[int, float]]: A dictionary containing the number of input tokens,
                                          output tokens, total tokens
        """
        if hasattr(response, "usage"):
            prompt_tokens = response.usage.input_tokens
            completion_tokens = response.usage.output_tokens
            total_tokens = prompt_tokens + completion_tokens

            tokens = {
                "input_tokens": prompt_tokens,
                "output_tokens": completion_tokens,
                "total_tokens": total_tokens,
            }
        else:
            tokens = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
            }
        return tokens
    
    def metadata(self, metadata: Dict[str, Union[str, float]]):
        """
        Set metadata for the current session.
        Args:
            metadata (Dict[str, Union[str, float]]): A dictionary containing metadata about the model
               - provider (str) | The provider of the model (e.g., "OpenAI", "Anthropic")
               - model (str) | The name of the model (e.g., "gpt-3.5-turbo", "claude-3-haiku-20240307")
               - input_cost_per_million_tokens (float) | Cost per million tokens for input
               - output_cost_per_million_tokens (float) | Cost per million tokens for output
        Raises:
            ValueError: If metadata is not provided or does not contain the required keys.
        Returns:
            None
        """
        try:
            if not isinstance(metadata, dict):
                print("Warning: NovaTrace metadata must be a dictionary")
                return
            
            self.provider = metadata.get('provider', None)
            self.model = metadata.get('model', None)
            self.input_cost_per_million_tokens = metadata.get('input_cost_per_million_tokens', 0.0)
            self.output_cost_per_million_tokens = metadata.get('output_cost_per_million_tokens', 0.0)

            if not all([self.provider, self.model, self.input_cost_per_million_tokens, self.output_cost_per_million_tokens]):
                print("Warning: NovaTrace metadata incomplete - some fields missing")
        except Exception as e:
            print(f"Warning: NovaTrace metadata configuration failed: {e}")

    def set_user(self, user_id: str = None, user_name: str = None):
        """
        Set default user information for traces.
        Args:
            user_id (str, optional): External user ID.
            user_name (str, optional): External user name.
        Returns:
            None
        """
        try:
            self.user_external_id = user_id or "guest_user"
            self.user_external_name = user_name or "Guest User"
        except Exception as e:
            print(f"Warning: NovaTrace set_user failed: {e}")

    def create_project(self, project_name: str):
        """
        Create a new project and associate the current session with it.
        If the project already exists, connects to it instead.
        Args:
            project_name (str): Name of the project to be created.
        Returns:
            Project: The project object.
        """
        try:
            if not self.session or not self.active_session:
                print("Warning: NovaTrace not properly initialized, cannot create project")
                return None
            
            # First try to connect to existing project (silently)
            existing_project = self.connect_to_project(project_name, silent=True)
            if existing_project:
                # Project exists and we're now connected to it
                if self.debug:
                    print(f"🔗 Connected to existing project '{project_name}'")
                return existing_project
            
            # Project doesn't exist, create a new one
            self.project = Project(
                name=project_name, 
                created_at=datetime.now(self.time_zone),
                updated_at=datetime.now(self.time_zone)
            )
            self.session.add(self.project)
            self.session.commit()
            
            # Associate current session with the new project
            self.active_session.project_id = self.project.id
            self.session.commit()
            
            if self.debug:
                print(f"✨ Created new project '{project_name}' and connected session")
            
            return self.project
            
        except Exception as e:
            print(f"Warning: NovaTrace create_project failed: {e}")
            return None

    def connect_to_project(self, project_name: str, silent: bool = False):
        """
        Connect to an existing project and associate the current session with it.
        If the project doesn't exist, creates it automatically.
        Args:
            project_name (str): Name of the project to connect to.
            silent (bool): If True, suppress messages.
        Returns:
            Project: The project object.
        """
        try:
            if not self.session or not self.active_session:
                if not silent:
                    print("Warning: NovaTrace not properly initialized, cannot connect to project")
                return None
                
            # Buscar proyecto globalmente (no por sesión)
            self.project = self.session.query(Project).filter_by(name=project_name).first()
            if not self.project:
                # Project doesn't exist, create it
                self.project = Project(
                    name=project_name, 
                    created_at=datetime.now(self.time_zone),
                    updated_at=datetime.now(self.time_zone)
                )
                self.session.add(self.project)
                self.session.commit()
                
                if not silent and self.debug:
                    print(f"✨ Created new project '{project_name}' (via connect_to_project)")
                
            # Asociar la sesión actual al proyecto
            self.active_session.project_id = self.project.id
            self.session.commit()
            
            if not silent:
                print(f"Connected to project '{project_name}' with session '{self.active_session.name}'")
            return self.project
        except Exception as e:
            if not silent:
                print(f"Warning: NovaTrace connect_to_project failed: {e}")
            return None

    def _get_named_args(self, func, *args, **kwargs):
        """
        Get named arguments from a function call with robust serialization.
        """
        try:
            sig = py_inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            def serialize_value(value):
                """Serialize a value with type information, handling complex objects safely"""
                try:
                    if value is None:
                        return {"type": "NoneType", "value": None}
                    elif isinstance(value, (str, int, float, bool)):
                        return {"type": type(value).__name__, "value": value}
                    elif isinstance(value, list):
                        # Para listas, limitar el número de elementos serializados
                        if len(value) <= 3:
                            serialized_list = []
                            for item in value:
                                try:
                                    serialized_list.append(serialize_value(item))
                                except:
                                    serialized_list.append({"type": "object", "value": str(item)[:100]})
                            return {"type": "list", "value": serialized_list}
                        else:
                            # Para listas grandes, solo serializar los primeros elementos
                            sample = []
                            for item in value[:2]:
                                try:
                                    sample.append(serialize_value(item))
                                except:
                                    sample.append({"type": "object", "value": str(item)[:100]})
                            return {"type": "list", "value": sample, "length": len(value), "truncated": True}
                    elif isinstance(value, dict):
                        # Para diccionarios, limitar el número de claves
                        if len(value) <= 5:
                            serialized_dict = {}
                            for k, v in value.items():
                                try:
                                    serialized_dict[str(k)] = serialize_value(v)
                                except:
                                    serialized_dict[str(k)] = {"type": "object", "value": str(v)[:100]}
                            return {"type": "dict", "value": serialized_dict}
                        else:
                            # Solo algunos elementos para diccionarios grandes
                            serialized_dict = {}
                            for k in list(value.keys())[:3]:
                                try:
                                    serialized_dict[str(k)] = serialize_value(value[k])
                                except:
                                    serialized_dict[str(k)] = {"type": "object", "value": str(value[k])[:100]}
                            return {"type": "dict", "value": serialized_dict, "total_keys": len(value), "truncated": True}
                    else:
                        # Para otros tipos, convertir a string pero limitando el tamaño
                        str_value = str(value)
                        if len(str_value) > 500:
                            str_value = str_value[:500] + "..."
                        return {"type": type(value).__name__, "value": str_value}
                except Exception as e:
                    # Fallback seguro para cualquier objeto problemático
                    return {"type": "unknown", "value": f"<Serialization error: {str(e)[:100]}>"}

            named_args = {}
            for name, value in bound_args.arguments.items():
                named_args[name] = serialize_value(value)
            
            return named_args
            
        except Exception as e:
            # Fallback más robusto que capture al menos los argumentos básicos
            fallback_args = {}
            try:
                # Intentar capturar kwargs al menos
                for key, value in kwargs.items():
                    try:
                        fallback_args[key] = {
                            "type": type(value).__name__,
                            "value": str(value)[:200] if not isinstance(value, (str, int, float, bool)) else value
                        }
                    except:
                        fallback_args[key] = {"type": "unknown", "value": "<unable to serialize>"}
                
                # Si hay args posicionales, intentar capturarlos con nombres genéricos
                if args:
                    for i, arg in enumerate(args):
                        try:
                            fallback_args[f"arg_{i}"] = {
                                "type": type(arg).__name__,
                                "value": str(arg)[:200] if not isinstance(arg, (str, int, float, bool)) else arg
                            }
                        except:
                            fallback_args[f"arg_{i}"] = {"type": "unknown", "value": "<unable to serialize>"}
                            
            except Exception:
                fallback_args = {"error": f"Failed to parse arguments: {str(e)[:100]}"}
            
            return fallback_args

    def _extract_user_info(self, func, *args, **kwargs):
        """
        Extract user information from function arguments.
        Looks for user_id, user_name, user, or context parameters.
        """
        try:
            sig = py_inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            user_id = None
            user_name = None
            
            # Strategy 1: Direct user_id and user_name parameters
            if 'user_id' in bound_args.arguments:
                user_id = bound_args.arguments['user_id']
            if 'user_name' in bound_args.arguments:
                user_name = bound_args.arguments['user_name']
                
            # Strategy 2: From user object
            if 'user' in bound_args.arguments:
                user_obj = bound_args.arguments['user']
                if hasattr(user_obj, 'id'):
                    user_id = user_obj.id
                elif hasattr(user_obj, 'user_id'):
                    user_id = user_obj.user_id
                if hasattr(user_obj, 'name'):
                    user_name = user_obj.name
                elif hasattr(user_obj, 'username'):
                    user_name = user_obj.username
                    
            # Strategy 3: From context object
            if 'context' in bound_args.arguments:
                context_obj = bound_args.arguments['context']
                if hasattr(context_obj, 'user_id'):
                    user_id = context_obj.user_id
                if hasattr(context_obj, 'user_name'):
                    user_name = context_obj.user_name
                elif hasattr(context_obj, 'user') and hasattr(context_obj.user, 'name'):
                    user_name = context_obj.user.name
                    
            # Strategy 4: From request object (web frameworks)
            if 'request' in bound_args.arguments:
                request_obj = bound_args.arguments['request']
                if hasattr(request_obj, 'user'):
                    if hasattr(request_obj.user, 'id'):
                        user_id = request_obj.user.id
                    if hasattr(request_obj.user, 'name'):
                        user_name = request_obj.user.name
                        
            # Strategy 5: From kwargs
            if user_id is None and 'user_id' in kwargs:
                user_id = kwargs['user_id']
            if user_name is None and 'user_name' in kwargs:
                user_name = kwargs['user_name']
                
            # Use defaults if not found
            if user_id is None:
                user_id = self.user_external_id
            if user_name is None:
                user_name = self.user_external_name
                
            return str(user_id) if user_id else None, str(user_name) if user_name else None
            
        except Exception as e:
            print(f"Warning: Could not extract user info: {e}")
            return self.user_external_id, self.user_external_name

    def _get_trace_type_id(self, type_name):
        """Get trace type ID by name with proper error handling."""
        try:
            if not self.session:
                return {"LLM": 1, "Agent": 2, "Tool": 3}.get(type_name, 1)
            trace_type = self.session.query(TraceTypes).filter_by(name=type_name).first()
            return trace_type.id if trace_type else {"LLM": 1, "Agent": 2, "Tool": 3}.get(type_name, 1)
        except Exception as e:
            print(f"Warning: NovaTrace _get_trace_type_id failed: {e}")
            # Handle database error and refresh session
            self._handle_db_error("_get_trace_type_id")
            # Return fallback value
            return {"LLM": 1, "Agent": 2, "Tool": 3}.get(type_name, 1)

    def _log_trace(self, type_id: int, input_data, output_data, request_time, response_time,
                    input_tokens=0, output_tokens=0, model_name=None, model_provider=None,
                    user_external_id=None, user_external_name=None):
        """
        Log a trace for the current request.
        Args:
            type_id (int): Type of trace (1 for LLM, 2 for Agent, 3 for Tool).
            input_data: Input data for the trace.
            output_data: Output data for the trace.
            request_time (datetime): Time when the request was made.
            response_time (datetime): Time when the response was received.
            input_tokens (int, optional): Number of input tokens used. Defaults to 0.
            output_tokens (int, optional): Number of output tokens used. Defaults to 0.
            user_external_id (str, optional): External user ID. Defaults to None.
            user_external_name (str, optional): External user name. Defaults to None.
        Returns:
            None
        Raises:
            None
        """
        try:
            if not self.session or not self.project or not self.active_session:
                print("Warning: NovaTrace not properly initialized, cannot log trace")
                return
                
            duration = (response_time - request_time).total_seconds() * 1000  # ms
            trace = Trace(
                type_id=type_id,
                input_data=json.dumps(input_data, default=str),
                output_data=json.dumps(output_data, default=str),
                project_id=self.project.id,
                session_id=self.active_session.id,  # Agregar referencia a la sesión
                created_at=response_time,
                request_time=request_time,
                response_time=response_time,
                duration_ms=duration,
                input_tokens=input_tokens,
                output_tokens=output_tokens,

                model_provider=model_provider if model_provider else self.provider,
                model_name=model_name if model_name else self.model,
                model_input_cost=self.input_cost_per_million_tokens,
                model_output_cost=self.output_cost_per_million_tokens,
                call_cost = ((input_tokens * (self.input_cost_per_million_tokens/1000000)) + (output_tokens * (self.output_cost_per_million_tokens/1000000))),
                
                # Add user information
                user_external_id=user_external_id,
                user_external_name=user_external_name
            )
            self.session.add(trace)
            self.session.commit()
        except Exception as e:
            print(f"Warning: NovaTrace _log_trace failed: {e}")
            # Handle database error and refresh session
            self._handle_db_error("_log_trace")
            
            # Try to log again with fresh session (one retry)
            try:
                if self.session and self.project and self.active_session:
                    duration = (response_time - request_time).total_seconds() * 1000  # ms
                    trace = Trace(
                        type_id=type_id,
                        input_data=json.dumps(input_data, default=str),
                        output_data=json.dumps(output_data, default=str),
                        project_id=self.project.id,
                        session_id=self.active_session.id,
                        created_at=response_time,
                        request_time=request_time,
                        response_time=response_time,
                        duration_ms=duration,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        model_provider=model_provider if model_provider else self.provider,
                        model_name=model_name if model_name else self.model,
                        model_input_cost=self.input_cost_per_million_tokens,
                        model_output_cost=self.output_cost_per_million_tokens,
                        call_cost = ((input_tokens * (self.input_cost_per_million_tokens/1000000)) + (output_tokens * (self.output_cost_per_million_tokens/1000000))),
                        user_external_id=user_external_id,
                        user_external_name=user_external_name
                    )
                    self.session.add(trace)
                    self.session.commit()
                    if self.debug:
                        print("NovaTrace: Successfully logged trace after session refresh")
            except Exception as retry_error:
                if self.debug:
                    print(f"NovaTrace: Failed to log trace after retry: {retry_error}")

    def llm(self, func):
        """
        Decorator to trace LLM calls.
        Args:
            func: The function to be traced.
        Returns:
            function: The wrapped function that logs the trace.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                request_time = datetime.now(self.time_zone)
                
                # Extract user information before function call
                user_id, user_name = self._extract_user_info(func, *args, **kwargs)
                
                result = func(*args, **kwargs)
                response_time = datetime.now(self.time_zone)
                
                # Obtener argumentos con la nueva lógica mejorada
                _args = self._get_named_args(func, *args, **kwargs)
                
                self._log_trace(self._get_trace_type_id("LLM"), {"args": _args},
                                result, request_time, response_time,
                                model_name=kwargs.get("model_name", self.model),
                                model_provider=kwargs.get("model_provider", self.provider),
                                input_tokens=kwargs.get("input_tokens", 0),
                                output_tokens=kwargs.get("output_tokens", 0),
                                user_external_id=user_id,
                                user_external_name=user_name
                                )
                return result
            except Exception as e:
                print(f"Warning: NovaTrace LLM decorator failed: {e}")
                # Return the original function result even if tracing fails
                try:
                    return func(*args, **kwargs)
                except:
                    # If even the original function fails, let it propagate
                    raise
        return wrapper

    def agent(self, func):
        """
        Decorator to trace agent calls.
        Args:
            func: The function to be traced.
        Returns:
            function: The wrapped function that logs the trace. 
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                request_time = datetime.now(self.time_zone)
                
                # Extract user information before function call
                user_id, user_name = self._extract_user_info(func, *args, **kwargs)
                
                result = func(*args, **kwargs)
                tokens = self.tokenizer(result)
                response_time = datetime.now(self.time_zone)
                
                # Obtener argumentos con la nueva lógica mejorada
                _args = self._get_named_args(func, *args, **kwargs)
                
                self._log_trace(self._get_trace_type_id("Agent"), {"args": _args}, 
                                result, request_time, response_time,
                                tokens.get("input_tokens", 0),
                                tokens.get("output_tokens", 0),
                                model_name=kwargs.get("model_name", self.model),
                                model_provider=kwargs.get("model_provider", self.provider),
                                user_external_id=user_id,
                                user_external_name=user_name
                                )
                return result
            except Exception as e:
                print(f"Warning: NovaTrace Agent decorator failed: {e}")
                # Return the original function result even if tracing fails
                try:
                    return func(*args, **kwargs)
                except:
                    # If even the original function fails, let it propagate
                    raise
        return wrapper

    def tool(self, func):
        """ 
        Decorator to trace tool calls.
        Args:
            func: The function to be traced.
        Returns:
            function: The wrapped function that logs the trace.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                request_time = datetime.now(self.time_zone)
                
                # Extract user information before function call
                user_id, user_name = self._extract_user_info(func, *args, **kwargs)
                
                result = func(*args, **kwargs)
                try:
                    result_raw = result[-1]['result']
                    result_text = result_raw[0].text if isinstance(result_raw, list) and result_raw else ""

                except Exception as e:
                    result_text = result

                response_time = datetime.now(self.time_zone)
                
                # Obtener argumentos con la nueva lógica mejorada
                _args = self._get_named_args(func, *args, **kwargs)
                
                self._log_trace(self._get_trace_type_id("Tool"), {"args": _args}, 
                                str(result_text), request_time, response_time,
                                user_external_id=user_id,
                                user_external_name=user_name
                                )
                return result
            except Exception as e:
                print(f"Warning: NovaTrace Tool decorator failed: {e}")
                # Return the original function result even if tracing fails
                try:
                    return func(*args, **kwargs)
                except:
                    # If even the original function fails, let it propagate
                    raise
        return wrapper
    
    def cleanup(self, force=False):
        """
        Clean up resources: stop API server and Docker container/Reflex process
        This method is idempotent and safe to call multiple times
        
        Args:
            force (bool): If True, forces cleanup even if interface is enabled
        """
        registry = get_registry()
        
        # Only cleanup interface resources if we're the owner and force=True
        if not self._is_interface_owner and not force:
            # Just close database session for non-owners
            try:
                if hasattr(self, 'session') and self.session:
                    self.session.close()
            except Exception:
                pass
            return
        
        # Only cleanup interface if forced or explicitly requested
        if not force and getattr(self, 'interface_enabled', False):
            # Just close database session, but keep interface running
            try:
                if hasattr(self, 'session') and self.session:
                    self.session.close()
            except Exception:
                pass
            return
        
        try:
            if getattr(self, 'debug', False):
                print("\n🛑 NovaTrace cleanup starting...")
            
            # Close database session
            if hasattr(self, 'session') and self.session:
                self.session.close()
            
            # Stop API server
            api_port = registry.get('api_port')
            if api_port:
                if getattr(self, 'debug', False):
                    print(f"   🔌 Stopping API server on port {api_port}")
                self._kill_process_on_port(api_port)
                registry['api_port'] = None
            
            # Stop web interface (Docker container or Reflex process)
            reflex_process = registry.get('reflex_process')
            if reflex_process:
                try:
                    # Try to stop Docker container first (React interface)
                    container_name = registry['container_name']
                    try:
                        subprocess.run([
                            "docker", "stop", container_name
                        ], capture_output=True, text=True, timeout=10)
                        
                        subprocess.run([
                            "docker", "rm", container_name
                        ], capture_output=True, text=True)
                        
                        if getattr(self, 'debug', False):
                            print("   🐳 Docker container stopped")
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
                        # Fallback to process termination (Reflex interface)
                        if hasattr(reflex_process, 'poll') and reflex_process.poll() is None:
                            # First try graceful termination
                            reflex_process.terminate()
                            
                            # Wait a bit for graceful shutdown
                            import time
                            time.sleep(2)
                            
                            # If still running, force kill
                            if reflex_process.poll() is None:
                                reflex_process.kill()
                            
                            if getattr(self, 'debug', False):
                                print("   🔄 Reflex process terminated")
                    
                    registry['reflex_process'] = None
                except Exception as e:
                    if getattr(self, 'debug', False):
                        print(f"   ⚠️  Interface cleanup warning: {e}")
            
            # Reset the registry
            registry['interface_enabled'] = False
            registry['interface_started'] = False
            
            if getattr(self, 'debug', False):
                print("   ✅ NovaTrace cleanup completed")
            
        except Exception as e:
            if getattr(self, 'debug', False):
                print(f"   ⚠️  Cleanup warning: {str(e)}")

    def __del__(self):
        """Destructor - ensure cleanup when object is destroyed"""
        try:
            self.cleanup()
        except:
            pass  # Ignore errors in destructor

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - automatic cleanup"""
        self.cleanup(force=True)

    def enable_signal_cleanup(self):
        """
        Enable signal handlers for cleanup (Ctrl+C, SIGTERM).
        Call this if you want the interface to close when user presses Ctrl+C.
        """
        import signal
        
        def signal_handler(signum, frame):
            print("\n🛑 Signal received, cleaning up NovaTrace...")
            self.cleanup(force=True)
            exit(0)
        
        try:
            signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
            signal.signal(signal.SIGTERM, signal_handler)  # Termination
        except AttributeError:
            # Some signals might not be available on all platforms
            pass

    def shutdown_all_interfaces(self):
        """
        Manually shutdown all NovaTrace web interfaces.
        Use this when you want to stop everything.
        """
        self.cleanup(force=True)

    def start_web_interface(self, force_rebuild=False):
        """
        Start the web interface with optional force rebuild
        
        Args:
            force_rebuild (bool): If True, forces Docker image rebuild
        """
        self.force_rebuild = force_rebuild
        return self._start_web_interface()
    
    def rebuild_web_interface(self):
        """
        Force rebuild the Docker image and restart the web interface
        """
        print("🔨 Force rebuilding NovaTrace web interface...")
        return self.start_web_interface(force_rebuild=True)

    def list_projects(self):
        """
        List all projects in the current session.
        """
        try:
            if not self.session or not self.active_session:
                print("Warning: NovaTrace not properly initialized, cannot list projects")
                return []
            return self.session.query(Project).filter_by(session_id=self.active_session.id).all()
        except Exception as e:
            print(f"Warning: NovaTrace list_projects failed: {e}")
            return []