import psutil
import platform
from datetime import datetime
import warnings

# Información del sistema operativo
def get_os_info():
    uname = platform.uname()
    return {
        "Sistema": uname.system,
        "Nombre del nodo": uname.node,
        "Versión": uname.version,
        "Release": uname.release,
        "Arquitectura": platform.machine(),
        "Procesador": uname.processor
    }

# Información de CPU
def get_cpu_info():
    return {
        "Cores físicos": psutil.cpu_count(logical=False),
        "Cores lógicos": psutil.cpu_count(logical=True),
        "Uso de CPU (%)": psutil.cpu_percent(interval=1)
    }

# Información de memoria RAM
def get_memory_info():
    mem = psutil.virtual_memory()
    return {
        "Total (GB)": round(mem.total / (1024 ** 3), 2),
        "Disponible (GB)": round(mem.available / (1024 ** 3), 2),
        "Uso (%)": mem.percent
    }

# Información del disco
def get_disk_info():
    disk = psutil.disk_usage('/')
    return {
        "Total (GB)": round(disk.total / (1024 ** 3), 2),
        "Usado (GB)": round(disk.used / (1024 ** 3), 2),
        "Libre (GB)": round(disk.free / (1024 ** 3), 2),
        "Uso (%)": disk.percent
    }