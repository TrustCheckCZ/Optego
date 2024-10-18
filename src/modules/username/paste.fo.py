import cfscrape
from bs4 import BeautifulSoup
from cli import Logger, PrintUtil
from plugins import Plugin, register_plugin
from urllib3.util.ssl_ import create_urllib3_context, DEFAULT_CIPHERS

@register_plugin
class GuildedAccountLookup(Plugin):
    plugin_type = 'username'

    def run(self, username):
        try:
            scraper = cfscrape.create_scraper()
            response = scraper.get(f'https://paste.fo/user/{username}')

            if response.status_code == 200:
                Logger.info('Paste.fo account found')
                
                soup = BeautifulSoup(response.text, 'html.parser')

                profile_data = {}

                user_info = soup.find('h4', class_='profileattribute')
                profile_data['Username'] = user_info.find('a').text
                profile_data['Cracked.io Profile'] = user_info.find('a')['href']

                discord_info = soup.find_all('h4', class_='profileattribute')[1]
                profile_data['Discord'] = discord_info.text.strip()

                telegram_info = soup.find_all('h4', class_='profileattribute')[2]
                profile_data['Telegram'] = telegram_info.find('a')['href']

                link_info = soup.find_all('h4', class_='profileattribute')[3]
                profile_data['External Website'] = link_info.find('a')['href']

                PrintUtil.prettify(profile_data)

                return profile_data
        except Exception as e:
            Logger.error(f'Error during the process: {e}')
