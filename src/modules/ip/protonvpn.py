import httpx
from cli import Logger, PrintUtil
from plugins import Plugin, register_plugin

@register_plugin
class ProtonVPNPlugin(Plugin):
    plugin_type = 'ip'

    def run(self, ip_address):
        request = httpx.get('https://api.protonmail.ch/vpn/logicals')
        data = request.json()
        for server in data.get('LogicalServers'):
            for host in server.get('Servers'):
                if ip_address == host.get('EntryIP'):
                    Logger.warning(f"This IP is an entry node for ProtonVPN | {server.get('Location')}")
                    PrintUtil.prettify(server)
                if ip_address == host.get('ExitIP'):
                    Logger.warning(f"This IP is an entry node for ProtonVPN | {server.get('Location')}")
                    PrintUtil.prettify(server)

    @classmethod
    def check(cls):
        return True  # Replace with actual check logic
