# Global registry to track running web interfaces
_web_interface_registry = {
    'api_port': None,
    'api_thread': None,
    'reflex_process': None,
    'container_name': 'novatrace-web',
    'instance_count': 0,
    'interface_enabled': False,
    'interface_started': False,
    'engine': None  # Engine personalizado para compartir con la webapp
}

def get_registry():
    """Get the global web interface registry"""
    return _web_interface_registry

def reset_registry():
    """Reset the global registry to initial state"""
    global _web_interface_registry
    _web_interface_registry = {
        'api_port': None,
        'api_thread': None,
        'reflex_process': None,
        'container_name': 'novatrace-web',
        'instance_count': 0,
        'interface_enabled': False,
        'interface_started': False,
        'engine': None
    }

def increment_instance_count():
    """Increment and return the instance count"""
    _web_interface_registry['instance_count'] += 1
    return _web_interface_registry['instance_count']
