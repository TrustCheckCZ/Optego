import argparse
from plugins import load_plugins, registered_plugins
from cli import ConsoleUtil, Logger

def run_plugins_by_type(plugin_type, target):
    if plugin_type in registered_plugins:
        plugin_classes = registered_plugins[plugin_type]
        
        for plugin_class in plugin_classes:
            plugin_instance = plugin_class()
            # Logger.info(f"Running {plugin_class.__name__} plugin for target: {target}")
            plugin_instance.run(target)
            Logger.nl()

    else:
        print(f"Error: No plugin of type '{plugin_type}' found.")

def main():
    ConsoleUtil.print_banner()

    parser = argparse.ArgumentParser(description="Run plugins from the modules folder.")
    parser.add_argument('--type', required=True, help="Specify the type of plugin (e.g., domain, username)")
    parser.add_argument('--target', required=True, help="Specify the target (e.g., domain name, username, IP)")
    
    args = parser.parse_args()

    load_plugins()

    run_plugins_by_type(args.type, args.target)

if __name__ == '__main__':
    main()
