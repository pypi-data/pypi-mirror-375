"""
NovaTrace API - FastAPI endpoints for web interface
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import jwt
import secrets
from pydantic import BaseModel
from ..database.model import Session as DBSession, Project, Trace, TraceTypes, User, sessionmaker
from ..database.model import engine as default_engine
from ..system_info import get_system_metrics, get_simple_metrics

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Pydantic models for request/response
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class UserResponse(BaseModel):
    id: int
    username: str
    is_active: bool
    created_at: str
    last_login: Optional[str] = None

class CreateUserRequest(BaseModel):
    username: str
    password: str
    is_active: bool = True

# Create FastAPI app
app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    title="NovaTrace API",
    version="1.2.3",
    description="Complete API for NovaTrace - AI Agent and LLM Tracing Platform. Monitor and analyze AI agents, LLM calls, and system performance.",
    contact={
        "name": "NovaTrace API Support",
        "email": "support@novatrace.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {"url": "http://localhost:4444", "description": "Development server"},
        {"url": "http://localhost:4445", "description": "Alternative development server"}
    ],
    tags_metadata=[
        {
            "name": "Authentication",
            "description": "User authentication and authorization endpoints. All other endpoints require Bearer token authentication.",
        },
        {
            "name": "Projects",
            "description": "Project management operations. Projects contain sessions and traces for organizing AI agent activities.",
        },
        {
            "name": "Sessions", 
            "description": "Session management within projects. Sessions group related traces and activities.",
        },
        {
            "name": "System",
            "description": "System monitoring and metrics endpoints for performance analysis.",
        },
        {
            "name": "Users",
            "description": "User management operations (admin only). Create, update, and manage user accounts.",
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
basic_security = HTTPBasic()

# Database dependency
def get_db():
    """Get database session"""
    # Importar el registro global desde el backend modularizado
    from ..backend.registry import get_registry
    
    # Usar el engine personalizado si está disponible, sino usar el por defecto
    registry = get_registry()
    engine = registry.get('engine', default_engine)
    SessionLocal = sessionmaker(bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(db: Session = Depends(get_db), username: str = Depends(verify_token)):
    """Get current authenticated user"""
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

def authenticate_docs(credentials: HTTPBasicCredentials = Depends(basic_security), db: Session = Depends(get_db)):
    """Authenticate user for documentation access using database"""
    # Query user from database
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not user.check_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials for documentation access",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return credentials.username

# Protected documentation endpoints
@app.get("/api/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(authenticate_docs)):
    """
    Protected Swagger UI documentation.
    
    Requires basic authentication to access API documentation.
    Uses the same user database as the main API authentication.
    """
    return get_swagger_ui_html(openapi_url="/api/openapi.json", title="NovaTrace API Documentation")

@app.get("/api/redoc", include_in_schema=False)
async def get_redoc_documentation(username: str = Depends(authenticate_docs)):
    """
    Protected ReDoc documentation.
    
    Requires basic authentication to access API documentation.
    Uses the same user database as the main API authentication.
    """
    from fastapi.openapi.docs import get_redoc_html
    return get_redoc_html(openapi_url="/api/openapi.json", title="NovaTrace API Documentation")

@app.get("/api/openapi.json", include_in_schema=False)
async def get_openapi_schema(username: str = Depends(authenticate_docs)):
    """
    Protected OpenAPI schema endpoint.
    
    Returns the OpenAPI schema for the API, requires authentication.
    Uses the same user database as the main API authentication.
    """
    return get_openapi(
        title="NovaTrace API",
        version="1.2.3",
        description="Complete API for NovaTrace - AI Agent and LLM Tracing Platform",
        routes=app.routes
    )

# Authentication endpoints
@app.post("/api/auth/login", response_model=LoginResponse, tags=["Authentication"])
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    User login and JWT token generation.
    
    Returns a JWT token that expires in 24 hours. Use this token in the Authorization header 
    for all subsequent API calls: `Authorization: Bearer <token>`
    
    - **username**: Your username (admin is the default superuser)
    - **password**: Your password
    """
    user = db.query(User).filter(User.username == login_data.username).first()

    if not user or not user.check_password(login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    # Update last login
    user.last_login = datetime.now()
    db.commit()
    
    access_token = create_access_token(data={"sub": user.username})
    return LoginResponse(
        access_token=access_token,
        username=user.username
    )

@app.get("/api/auth/me", response_model=UserResponse, tags=["Authentication"])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Returns details about the currently authenticated user including:
    - User ID and username
    - Account status (active/inactive)  
    - Account creation date
    - Last login timestamp
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        is_active=current_user.is_active,
        created_at=current_user.created_at.isoformat(),
        last_login=current_user.last_login.isoformat() if current_user.last_login else None
    )

@app.post("/api/auth/change-password", tags=["Authentication"])
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change the current user's password.
    
    Requires the current password for verification before setting the new password.
    
    - **current_password**: Your current password for verification
    - **new_password**: The new password to set
    """
    if not current_user.check_password(password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user.set_password(password_data.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}

# User management endpoints (admin only)
def check_admin_user(current_user: User = Depends(get_current_user)):
    """Check if current user is admin"""
    if current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can perform this action"
        )
    return current_user

@app.get("/api/users", response_model=List[UserResponse], tags=["Users"])
async def get_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(check_admin_user)
):
    """
    Get all users (admin only).
    
    Returns a list of all users in the system with their details.
    Only accessible by admin users.
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
        for user in users
    ]

@app.post("/api/users", response_model=UserResponse, tags=["Users"])
async def create_user(
    user_data: CreateUserRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(check_admin_user)
):
    """
    Create a new user (admin only).
    
    Creates a new user account with the specified username and password.
    Only accessible by admin users.
    
    - **username**: Unique username for the new user
    - **password**: Password for the new user
    - **is_active**: Whether the user account is active (default: true)
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        is_active=user_data.is_active
    )
    new_user.set_password(user_data.password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        is_active=new_user.is_active,
        created_at=new_user.created_at.isoformat(),
        last_login=None
    )

class UpdateUserRequest(BaseModel):
    is_active: bool

@app.put("/api/users/{user_id}", tags=["Users"])
async def update_user(
    user_id: int,
    user_data: UpdateUserRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(check_admin_user)
):
    """
    Update user status (admin only).
    
    Updates the active status of a user account. Admins cannot deactivate their own account.
    Only accessible by admin users.
    
    - **user_id**: ID of the user to update
    - **is_active**: New active status for the user
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deactivating themselves
    if user.id == admin_user.id and not user_data.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account"
        )
    
    user.is_active = user_data.is_active
    db.commit()
    
    return {"message": "User updated successfully"}

@app.delete("/api/users/{user_id}", tags=["Users"])
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(check_admin_user)
):
    """
    Delete user (admin only).
    
    Permanently deletes a user account. Admins cannot delete their own account.
    Only accessible by admin users.
    
    - **user_id**: ID of the user to delete
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from deleting themselves
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "NovaTrace API is running", "status": "healthy"}

@app.get("/api/sessions", tags=["Sessions"])
async def get_sessions(project_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get all sessions, optionally filtered by project.
    
    Returns a list of sessions with their metadata and trace counts.
    Sessions can be filtered by project ID.
    
    - **project_id** (optional): Filter sessions by specific project ID
    """
    try:
        query = db.query(DBSession)
        if project_id:
            query = query.filter(DBSession.project_id == project_id)
        
        sessions = query.order_by(desc(DBSession.created_at)).all()
        return {
            "sessions": [
                {
                    "id": session.id,
                    "name": session.name,
                    "project_id": session.project_id,
                    "project_name": session.project.name if session.project else None,
                    "created_at": session.created_at.isoformat(),
                    "trace_count": db.query(Trace).filter(Trace.session_id == session.id).count()
                }
                for session in sessions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sessions: {str(e)}")

@app.get("/api/projects", tags=["Projects"])
async def get_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    Get all projects with their sessions and metrics.
    
    Returns a comprehensive list of all projects including:
    - Basic project information (name, description, status)
    - Associated sessions and their trace counts  
    - Performance metrics (cost, tokens, duration)
    - Resource usage indicators (CPU, memory simulation)
    - Recent activity indicators
    
    Projects are ordered by most recent activity first.
    """
    try:
        # Ordenar proyectos por última actividad (updated_at) y luego por creación, más reciente primero
        projects = db.query(Project).order_by(desc(Project.updated_at), desc(Project.created_at)).all()
        
        result = []
        for project in projects:
            # Get all sessions for this project - ordenadas del más reciente al más viejo
            sessions = db.query(DBSession).filter(DBSession.project_id == project.id).order_by(desc(DBSession.created_at)).all()
            
            # Calculate metrics for ALL traces in this project (across all sessions)
            traces = db.query(Trace).filter(Trace.project_id == project.id).order_by(desc(Trace.created_at)).all()
            
            total_cost = sum(trace.call_cost or 0 for trace in traces)
            total_tokens = sum((trace.input_tokens or 0) + (trace.output_tokens or 0) for trace in traces)
            avg_duration = sum(trace.duration_ms or 0 for trace in traces) / len(traces) if traces else 0
            
            # Get recent activity (last 24 hours) across all sessions
            recent_activity = db.query(Trace).filter(
                Trace.project_id == project.id,
                Trace.created_at >= datetime.now() - timedelta(hours=24)
            ).count()
            
            # Determine status based on recent activity
            status = "active" if recent_activity > 0 else "inactive"
            if recent_activity > 10:
                status = "running"
            elif recent_activity > 0:
                status = "idle"
            else:
                status = "stopped"
            
            result.append({
                "id": project.id,
                "name": project.name,
                "description": project.description or f"Project with {len(sessions)} sessions and {len(traces)} traces",
                "sessions": [
                    {
                        "id": session.id,
                        "name": session.name,
                        "created_at": session.created_at.isoformat(),
                        "traces_count": len([t for t in traces if t.session_id == session.id])
                    }
                    for session in sessions
                ],
                "status": status,
                "type": "llm_project",
                "created": project.created_at.isoformat() if project.created_at else datetime.now().isoformat(),
                "lastModified": max(trace.created_at for trace in traces if trace.created_at).isoformat() if traces and any(trace.created_at for trace in traces) else (project.created_at.isoformat() if project.created_at else datetime.now().isoformat()),
                "metrics": {
                    "total_traces": len(traces),
                    "total_sessions": len(sessions),
                    "total_cost": round(total_cost, 4),
                    "total_tokens": total_tokens,
                    "avg_duration_ms": round(avg_duration, 2),
                    "recent_activity": recent_activity
                },
                "cpu": min(recent_activity * 2, 100),  # Simulate CPU based on activity
                "memory": min(len(traces) * 10, 1000),  # Simulate memory based on traces
            })
        
        return {"projects": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching projects: {str(e)}")

@app.get("/api/projects/{project_id}", tags=["Projects"])
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Get specific project details with traces.
    
    Returns detailed information about a specific project including:
    - Project metadata and creation date
    - Comprehensive metrics breakdown by trace type
    - Recent traces (up to 50 most recent)
    - Associated session information
    - Cost and token usage analytics
    
    - **project_id**: The ID of the project to retrieve
    """
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Obtener traces ordenadas del más reciente al más viejo
        traces = db.query(Trace).filter(Trace.project_id == project_id).order_by(desc(Trace.created_at)).all()
        
        # Get all session names in a single query
        session_ids = [trace.session_id for trace in traces if trace.session_id]
        sessions_dict = {}
        if session_ids:
            sessions = db.query(DBSession).filter(DBSession.id.in_(session_ids)).order_by(desc(DBSession.created_at)).all()
            sessions_dict = {session.id: session.name for session in sessions}
        
        # Calculate detailed metrics
        total_cost = sum(trace.call_cost or 0 for trace in traces)
        total_tokens = sum((trace.input_tokens or 0) + (trace.output_tokens or 0) for trace in traces)
        
        # Group by trace type
        trace_types = {}
        for trace in traces:
            trace_type = db.query(TraceTypes).filter(TraceTypes.id == trace.type_id).first()
            type_name = trace_type.name if trace_type else "Unknown"
            
            if type_name not in trace_types:
                trace_types[type_name] = {"count": 0, "cost": 0, "tokens": 0}
            
            trace_types[type_name]["count"] += 1
            trace_types[type_name]["cost"] += trace.call_cost or 0
            trace_types[type_name]["tokens"] += (trace.input_tokens or 0) + (trace.output_tokens or 0)
        
        return {
            "id": project.id,
            "name": project.name,
            "created": project.created_at.isoformat(),
            "metrics": {
                "total_traces": len(traces),
                "total_cost": round(total_cost, 4),
                "total_tokens": total_tokens,
                "trace_types": trace_types
            },
            "traces": [
                {
                    "id": trace.id,
                    "trace_id": f"trace_{trace.id}",
                    "type": trace.type_id,
                    "created_at": trace.created_at.isoformat(),
                    "timestamp": trace.created_at.isoformat(),
                    "duration_ms": trace.duration_ms,
                    "cost": trace.call_cost,
                    "tokens": (trace.input_tokens or 0) + (trace.output_tokens or 0),
                    "input_tokens": trace.input_tokens,
                    "output_tokens": trace.output_tokens,
                    "user_id": trace.user_external_id,
                    "user_name": trace.user_external_name,
                    "session_id": trace.session_id,
                    "session_name": sessions_dict.get(trace.session_id, None) if trace.session_id else None,
                    "model_provider": trace.model_provider,
                    "model_name": trace.model_name,
                    "input_data": trace.input_data,
                    "output_data": trace.output_data,
                    "status": "completed"  # Default status for existing traces
                }
                for trace in traces[:50]  # Primeras 50 trazas (más recientes ya que están ordenadas desc)
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching project: {str(e)}")

@app.get("/api/projects/{project_id}/metrics", tags=["Projects"])
async def get_project_metrics(project_id: int, db: Session = Depends(get_db)):
    """
    Get project metrics and historical data.
    
    Returns time-series metrics for a project including:
    - Hourly aggregated data for the last 24 hours
    - Trace counts, costs, tokens, and average durations
    - Summary statistics across all time periods
    
    Useful for creating charts and analyzing project performance over time.
    
    - **project_id**: The ID of the project to get metrics for
    """
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Obtener traces ordenadas del más reciente al más viejo
        traces = db.query(Trace).filter(Trace.project_id == project_id).order_by(desc(Trace.created_at)).all()
        
        # Calculate metrics by hour for the last 24 hours
        hourly_data = {}
        for trace in traces:
            hour = trace.created_at.replace(minute=0, second=0, microsecond=0)
            hour_str = hour.isoformat()
            
            if hour_str not in hourly_data:
                hourly_data[hour_str] = {
                    "traces": 0,
                    "cost": 0,
                    "tokens": 0,
                    "avg_duration": 0,
                    "durations": []
                }
            
            hourly_data[hour_str]["traces"] += 1
            hourly_data[hour_str]["cost"] += trace.call_cost or 0
            hourly_data[hour_str]["tokens"] += (trace.input_tokens or 0) + (trace.output_tokens or 0)
            hourly_data[hour_str]["durations"].append(trace.duration_ms or 0)
        
        # Calculate averages
        for hour_data in hourly_data.values():
            if hour_data["durations"]:
                hour_data["avg_duration"] = sum(hour_data["durations"]) / len(hour_data["durations"])
            del hour_data["durations"]  # Remove raw data
        
        # Ordenar datos horarios del más reciente al más viejo
        sorted_hourly_data = dict(sorted(hourly_data.items(), reverse=True))
        
        return {
            "project_id": project_id,
            "hourly_data": sorted_hourly_data,
            "summary": {
                "total_traces": len(traces),
                "total_cost": sum(trace.call_cost or 0 for trace in traces),
                "total_tokens": sum((trace.input_tokens or 0) + (trace.output_tokens or 0) for trace in traces),
                "avg_duration": sum(trace.duration_ms or 0 for trace in traces) / len(traces) if traces else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching project metrics: {str(e)}")

@app.get("/api/system/metrics", tags=["System"])
async def get_system_metrics_endpoint():
    """
    Get current system metrics.
    
    Returns real-time system performance metrics including:
    - CPU usage percentage
    - Memory utilization  
    - Disk usage statistics
    - Network activity
    
    Falls back to simulated data if system monitoring is unavailable.
    """
    try:
        metrics = get_system_metrics()
        return {
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        # Fallback to simulated data if system monitoring fails
        import random
        return {
            "metrics": {
                "cpu": {"usage": random.randint(20, 80)},
                "memory": {"percent": random.randint(40, 90)},
                "disk": {"percent": random.randint(30, 85)},
                "network": {"bytes_sent": random.randint(1000, 10000)}
            },
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/api/system/simple-metrics", tags=["System"])
async def get_simple_system_metrics():
    """
    Get simplified system metrics for dashboard.
    
    Returns essential system metrics optimized for dashboard display:
    - CPU and memory usage percentages
    - Disk usage percentage
    - System uptime in seconds
    - Current process memory usage
    
    This endpoint doesn't require authentication and provides fallback values.
    """
    try:
        metrics = get_simple_metrics()
        return {
            "cpu_usage": metrics["cpu_usage"],
            "memory_usage": metrics["memory_usage"], 
            "disk_usage": metrics["disk_usage"],
            "uptime": metrics["uptime"],
            "process_memory": metrics["process_memory"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        # Return fallback values instead of error
        return {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "uptime": 0,
            "process_memory": 0.0,
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.get("/api/system/status", tags=["System"])
async def get_system_status(db: Session = Depends(get_db)):
    """
    Get system status information.
    
    Returns comprehensive system status including:
    - System uptime and load averages
    - Available memory and disk space
    - Database statistics (projects, sessions, traces)
    - Recent activity indicators (last 24 hours)
    
    Useful for monitoring overall system health and usage patterns.
    """
    try:
        # Count totals
        total_sessions = db.query(DBSession).count()
        total_projects = db.query(Project).count()
        total_traces = db.query(Trace).count()
        
        # Recent activity (last 24 hours)
        recent_traces = db.query(Trace).filter(
            Trace.created_at >= datetime.now() - timedelta(hours=24)
        ).count()
        
        return {
            "uptime": "15 days, 8 hours",  # TODO: Calculate real uptime
            "active_processes": 247,  # TODO: Get real process count
            "load_average": "1.24, 1.18, 1.09",  # TODO: Get real load
            "free_memory": "2.4 GB",  # TODO: Get real memory
            "free_disk": "145.2 GB",  # TODO: Get real disk space
            "statistics": {
                "total_sessions": total_sessions,
                "total_projects": total_projects,
                "total_traces": total_traces,
                "recent_activity": recent_traces
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching system status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=4444)
