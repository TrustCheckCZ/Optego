import httpx
import hashlib
from cli import Logger, PrintUtil
from plugins import Plugin, register_plugin

@register_plugin
class GravatarPlugin(Plugin):
    plugin_type = 'email'

    def run(self, email):
        hashed_name = hashlib.md5(email.encode()).hexdigest()

        request = httpx.get(f'https://en.gravatar.com/{hashed_name}.json')

        try:
            data = request.json()
            if data == 'User not found': return False

            user = data['entry'][0]
            user.pop('requestHash')

            PrintUtil.prettify(user)
        except Exception as e:
            Logger.error(f'Failed to grab gravatar infomation, {e}')
                
    @classmethod
    def check(cls):
        return True  # Replace with actual check logic
