from sqlalchemy import create_engine
from decouple import config as deconfig

from datetime import datetime
import pytz
import os

hora = pytz.utc

def _find_connect_db():
    """Crear connect.db en el directorio de trabajo actual."""
    current_dir = os.getcwd()
    db_path = os.path.join(current_dir, 'connect.db')
    return db_path

# Buscar dinámicamente la base de datos
db_path = _find_connect_db()
database_url = f"sqlite:///{db_path}"

#engine a sqlite
engine = create_engine(deconfig("DATABASE_URL", default=database_url))