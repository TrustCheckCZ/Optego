import cfscrape
from bs4 import BeautifulSoup
from fake_headers import Headers
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context, DEFAULT_CIPHERS
from plugins import Plugin, register_plugin
from cli import Logger, PrintUtil

DEFAULT_CIPHERS += ':!SHA1'

class CustomAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = create_urllib3_context(ciphers=DEFAULT_CIPHERS)
        super(CustomAdapter, self).init_poolmanager(*args, ssl_context=ctx, **kwargs)

@register_plugin
class TwitterRecoveryPlugin(Plugin):
    plugin_type = 'email'

    @classmethod
    def check(cls):
        return True

    def run(self, account):
        try:
            header = Headers(browser="chrome", os="win", headers=True)

            scraper = cfscrape.create_scraper()
            scraper.mount('https://', CustomAdapter())

            url = "https://twitter.com/account/begin_password_reset"

            req = scraper.get(url, headers=header.generate())
            soup = BeautifulSoup(req.text, 'html.parser')

            authenticity_token = soup.find('input', {'name': 'authenticity_token'}).get('value')

            data = {
                'authenticity_token': authenticity_token,
                'account_identifier': account
            }

            response = scraper.post(url, cookies=req.cookies, data=data, headers=header.generate())
            soup2 = BeautifulSoup(response.text, 'html.parser')

            error = "We couldn't find your account with that information" in soup2
            ratelimit = "Please try again later." in soup2

            if error: return
            if ratelimit:
                Logger.error(f"Ratelimited from twitter, change your IP to continue using this module.")

            if "Verify your identity by entering the username associated with your X account." in str(soup2):
                Logger.info("User has 2FA Enabled.")
                return

            try:
                info = soup2.find('ul', class_='Form-radioList').find_all("strong")
            except:
                info = None

            if not info: return

            output = {}

            if len(info) == 2:
                output["Recovery Address"] = info[0].text.strip()
                output["Recovery Phone"]   = '*'*8 + str(info[1].text.strip())
            else:
                output["Recovery Address"] = info[0].text.strip()

            Logger.info(f"Found recovery info from twitter.com")
            PrintUtil.prettify(output)

        except Exception as e:
            Logger.error(f"An error occurred: {str(e)}")
