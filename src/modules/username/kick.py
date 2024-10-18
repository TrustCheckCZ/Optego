import cfscrape
from bs4 import BeautifulSoup
from fake_headers import Headers
from cli import Logger, PrintUtil
from requests.adapters import HTTPAdapter
from plugins import Plugin, register_plugin
from urllib3.util.ssl_ import create_urllib3_context, DEFAULT_CIPHERS

@register_plugin
class GuildedAccountLookup(Plugin):
    plugin_type = 'username'

    def run(self, username):
        try:
            scraper = cfscrape.create_scraper()
            response = scraper.get(f'https://www.guilded.gg/api/search?query={username}&entityType=user')

            if response.status_code == 200:
                data = response.json()
                users = data.get('results', {}).get('users')

                Logger.info('Possible Guilded users found')
                PrintUtil.prettify(users)

                return data
        except Exception as e:
            Logger.error(f'Error during the process: {e}')
