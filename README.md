<div align="center" style="margin-bottom: 15px;">
  <img src="https://github.com/TrustCheckCZ/Optego/blob/main/_images/logo.png?raw=true" width="120" alt="Optego Logo">
</div>

---

# Optego

**Optego** is an open-source alternative to the commercial [Maltego](https://www.paterva.com/) project, providing powerful tools for data collection and analysis with a modular and customizable approach.

## Features
- Modular architecture with support for custom plugins.
- Multiple pre-built modules for various data types (e.g., email scanning, domain analysis).
- Fully open-source and easily extensible for additional use cases.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/TrustCheckCZ/Optego.git
    ```
2. Navigate to the project directory:
    ```bash
    cd Optego
    ```
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To use Optego, simply run the following command:

```bash
python optego.py --type <module_type> --target <target>
```

## Example
```
python optego.py --type email --target example@gmail.com
```

## Modules
Optego supports custom plugins, allowing you to easily extend its functionality. Below is an example of how to create your own module:
### Example Plugin

1. **Create your custom module:** Define your plugin in the plugins directory `/plugins/example`.
2. **Register your plugin:** Use the @register_plugin decorator to integrate your module with Optego.

```python
from cli import Logger
from plugins import Plugin, register_plugin

@register_plugin
class ExamplePlugin(Plugin):
    plugin_type = 'your_plugin_type'

    def run(self, domain):
        Logger.info(f"Running domain plugin for {domain}")
        # Your module's functionality here.

    @classmethod
    def check(cls):
        return True  # Replace with logic to verify the plugin's execution.
```
