import os
import importlib.util
import inspect
from cli import Logger

registered_plugins = {}

def register_plugin(cls):
    if cls.plugin_type not in registered_plugins:
        registered_plugins[cls.plugin_type] = []
    
    if cls not in registered_plugins[cls.plugin_type]:
        registered_plugins[cls.plugin_type].append(cls)
        # Bloat Registering output
        # Logger.info(f'Registered plugin: {cls.__name__} [{cls.plugin_type}]')
    return cls

class Plugin:
    plugin_type = None  # This will be overridden by subclasses don't remove

    def __init__(self):
        pass

    def run(self, *args, **kwargs):
        raise NotImplementedError("Plugins must implement the run method.")

    @classmethod
    def check(cls):
        raise NotImplementedError("Plugins must implement the check method.")

def load_plugins():
    modules_folder = os.path.join(os.path.dirname(__file__), "modules")
    
    for root, dirs, files in os.walk(modules_folder):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_path = os.path.join(root, file)
                load_plugin_from_file(module_path)

def load_plugin_from_file(module_path):
    module_name = module_path.replace(os.path.sep, '.').replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for name, obj in inspect.getmembers(module, inspect.isclass):
        if issubclass(obj, Plugin) and obj is not Plugin:
            register_plugin(obj)
            Logger.info(f'Loaded module: {module_path}')

    Logger.nl()