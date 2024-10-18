import argparse, uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from plugins import load_plugins, registered_plugins
from cli import Logger, ConsoleUtil

app = FastAPI()

# Serve static files (optional if needed for future use)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Startup event to load plugins before handling requests
@app.on_event("startup")
async def startup_event():
    Logger.info("Loading plugins at startup...")
    load_plugins()  # Ensure plugins are loaded before API requests

# Serve the HTML form for running plugins
@app.get("/", response_class=HTMLResponse)
async def get_form():
    with open("templates/index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

class PluginRequest(BaseModel):
    plugin_type: str
    target: str

@app.post("/run-plugin/")
async def run_plugin(request: PluginRequest):
    plugin_type = request.plugin_type
    target = request.target

    if plugin_type in registered_plugins:
        plugin_classes = registered_plugins[plugin_type]
        results = []  # To collect results from each plugin

        for plugin_class in plugin_classes:
            plugin_instance = plugin_class()
            result = plugin_instance.run(target)  # Capture plugin result
            if result != False and result != None:
                results.append({'plugin_name': plugin_class.__name__, 'data': result})  # Add result to results list

            Logger.nl()

        return {
            "status": "success",
            "message": f"Plugins of type '{plugin_type}' run for target '{target}'",
            "results": results  # Include the collected results in the response
        }
    else:
        return {"status": "error", "message": f"No plugin of type '{plugin_type}' found."}

def run_plugins_by_type(plugin_type, target):
    if plugin_type in registered_plugins:
        plugin_classes = registered_plugins[plugin_type]
        
        for plugin_class in plugin_classes:
            plugin_instance = plugin_class()
            plugin_instance.run(target)
            Logger.nl()

    else:
        Logger.error(f"Error: No plugin of type '{plugin_type}' found.")

def main():
    ConsoleUtil.print_banner()

    parser = argparse.ArgumentParser(description="Run plugins from the modules folder.")
    parser.add_argument('--type', help="Specify the type of plugin (e.g., domain, username)")
    parser.add_argument('--target', help="Specify the target (e.g., domain name, username, IP)")
    parser.add_argument('--web', action='store_true', help="Run the plugins via a web server instead of CLI")
    
    args = parser.parse_args()

    load_plugins()

    if args.web:
        script_name = __name__
        Logger.info("Starting web server...")
        uvicorn.run(f"{script_name}:app", host="127.0.0.1", port=8000, reload=True)
    elif args.type and args.target:
        run_plugins_by_type(args.type, args.target)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
