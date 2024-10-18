import httpx
from bs4 import BeautifulSoup
from cli import Logger, PrintUtil
from plugins import Plugin, register_plugin
import re
import time

@register_plugin
class KikEmailResolver(Plugin):
    plugin_type = 'username'

    def run(self, username):
        try:
            response = httpx.get(f'https://kik.me/{username}')

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                display_name_tag = soup.find('h1', class_='display-name')
                display_user_tag = soup.find('h2', class_='username')
                
                if display_name_tag and display_user_tag:
                    display_name = display_name_tag.text.strip()
                    display_user = display_user_tag.text.strip()

                    Logger.info('Recovered Kik.com user')
                    PrintUtil.prettify({
                        'Name': display_name,
                        'username': display_user,
                    })
                else:
                    Logger.error('Failed to recover user details (image might not have loaded)')

                data = {'emailOrUsername': username}
                request = httpx.post('https://ws.kik.com/p', data=data, headers={
                    'Accept-Language': 'en-US,en;q=0.8',
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.120 Chrome/37.0.2062.120 Safari/537.36'
                })

                if request.status_code == 200:
                    post_soup = BeautifulSoup(request.text, 'html.parser')
                    paragraphs = post_soup.find_all('p')

                    email = None
                    for p in paragraphs:
                        possible_email = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', p.text)
                        if possible_email:
                            email = possible_email.group()
                            break

                    if email:
                        Logger.info('Recovered Kik.com email')
                        PrintUtil.prettify({'Recovery Email': email})

                        return {'Recovery Email': email}
                    else:
                        Logger.warning('No email found')

            else:
                Logger.error(f'Failed to fetch user page, status code: {response.status_code}')

        except Exception as e:
            Logger.error(f'Error during the process: {e}')

    @classmethod
    def check(cls):
        return True  # Replace with actual check logic
