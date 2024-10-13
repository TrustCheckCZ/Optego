import httpx
from cli import Logger, PrintUtil
from plugins import Plugin, register_plugin

@register_plugin
class TitterPhoneCheckPlugin(Plugin):
    plugin_type = 'phone'

    def run(self, phone_number):
        try:
            api_url = 'https://x.com/i/api/1.1/users/phone_number_available.json'
            
            params = {
                'raw_phone_number': phone_number,
                'country_code': 'US' # TODO: Add auto-country code
            }
            
            response = httpx.get(api_url, params=params)

            if response.status_code == 200:
                data = response.json()
                
                if data.get('valid', False):
                    Logger.info(f'Phone number {phone_number} is valid and not registered on X.com.')
                    PrintUtil.prettify({'Phone Number': phone_number, 'Status': 'Not Registered'})
                else:
                    Logger.warning(f'Phone number {phone_number} is already registered on X.com.')
                    PrintUtil.prettify({'Phone Number': phone_number, 'Status': 'Registered'})
            else:
                Logger.error(f'Failed to check phone number, status code: {response.status_code}')
                Logger.error(f'Response: {response.text}')

        except Exception as e:
            Logger.error(f'Error during the process: {e}')

    @classmethod
    def check(cls):
        return True
