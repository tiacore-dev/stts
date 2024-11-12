# service_registry.py
registry = {}

def register_service(name, service):
    registry[name] = service

def get_service(name):
    return registry.get(name)
