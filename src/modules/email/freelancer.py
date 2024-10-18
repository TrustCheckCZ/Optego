import httpx
from cli import Logger, PrintUtil
from plugins import Plugin, register_plugin

@register_plugin
class FreeLancerRecoveryPlugin(Plugin):
    plugin_type = 'email'

    def run(self, email):
        response = httpx.post('https://www.freelancer.com/auth/forgot', data = {'email': email})
        if response.status_code == 200:
            data = response.json()
            _type = data.get('result', None)
            if _type and _type.get('action') == 'account_reactivation':
                Logger.info('Deactivated freelancer.com account found')
                PrintUtil.prettify({'User ID': _type.get('user_id')})

                return {'User ID': _type.get('user_id')}

    @classmethod
    def check(cls):
        return True  # Replace with actual check logic
