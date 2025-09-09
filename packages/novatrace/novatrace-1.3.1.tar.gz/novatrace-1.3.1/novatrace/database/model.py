from sqlalchemy import Integer, String, DateTime, ForeignKey, Float, BIGINT, Text, JSON, Boolean
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Table
from datetime import datetime
import bcrypt

from novatrace.connect import *

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(hora))
    last_login = Column(DateTime, nullable=True)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)
    project_id = Column(Integer, ForeignKey("projects.id"))  # Una sesión pertenece a un proyecto
    created_at = Column(DateTime, default=lambda: datetime.now(hora))
    
    project = relationship("Project", back_populates="sessions")
    traces = relationship("Trace", back_populates="session")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)  # Los proyectos ahora son únicos
    description = Column(String(500), nullable=True)  # Agregar descripción opcional
    created_at = Column(DateTime, default=lambda: datetime.now(hora))
    updated_at = Column(DateTime, default=lambda: datetime.now(hora), onupdate=lambda: datetime.now(hora))

    sessions = relationship("Session", back_populates="project")  # Un proyecto tiene muchas sesiones
    traces = relationship("Trace", back_populates="project")

class TraceTypes(Base):
    __tablename__ = "trace_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)

    traces = relationship("Trace", back_populates="trace_types")

class Trace(Base):
    __tablename__ = "traces"
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey("trace_types.id"))
    input_data = Column(Text, nullable=False)
    output_data = Column(Text, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    session_id = Column(Integer, ForeignKey("sessions.id"))  # Referencia directa a la sesión
    created_at = Column(DateTime, default=lambda: datetime.now(hora))
    request_time = Column(DateTime, nullable=False)    # cuando se recibe el input
    response_time = Column(DateTime, nullable=False)   # cuando se genera output
    duration_ms = Column(Float, nullable=False)      

    user_external_id = Column(String(255), nullable=True)  # ID del usuario de el proyecto
    user_external_name = Column(String(255), nullable=True)  # nombre del usuario de el proyecto
    model_provider = Column(String(255), nullable=True)  # proveedor del modelo (ej. "anthropic", "openai")
    model_name = Column(String(255), nullable=True)  # nombre del modelo utilizado (ej. "claude-3-haiku-20240307", "gpt-4-turbo")
    model_input_cost = Column(Float, nullable=True)  # costo por token de entrada del modelo
    model_output_cost = Column(Float, nullable=True)  # costo por token de salida del
    call_cost = Column(Float, nullable=True)  # costo total de la llamada (input + output)

    input_tokens = Column(BIGINT, nullable=True)  # tokens de entrada
    output_tokens = Column(BIGINT, nullable=True)  # tokens de salida 

    project = relationship("Project", back_populates="traces")
    session = relationship("Session", back_populates="traces")
    trace_types = relationship("TraceTypes", back_populates="traces")

