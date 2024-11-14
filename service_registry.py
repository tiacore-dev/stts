# service_registry.py
registry = {}

def register_service(name, service):
    registry[name] = service
    print(f"Service registered: {name}")  # Вывод при регистрации сервиса

def get_service(name):
    service = registry.get(name)
    if service is None:
        print(f"Error: Service '{name}' not found!")  # Вывод ошибки, если сервис не найден
    return service
