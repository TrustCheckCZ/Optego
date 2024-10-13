import re
import httpx
from cli import Logger, PrintUtil
from datetime import datetime
from plugins import Plugin, register_plugin

@register_plugin
class ProtonPlugin(Plugin):
    plugin_type = 'email'

    def run(self, email):
        request = httpx.get(f'https://api.protonmail.ch/pks/lookup?op=index&search={email}')
        bodyResponse = request.text.rstrip()

        accountNotFound = "info:1:0" # not valid account

        if bodyResponse == accountNotFound:
            return
        
        Logger.info('Protonmail account found')
        regexPattern1 = "2048:(.*)::" # RSA 2048-bit (Older but faster)
        regexPattern2 = "4096:(.*)::" # RSA 4096-bit (Secure but slow)
        regexPattern3 = "22::(.*)::"  # X25519 (Modern, fastest, secure)

        try:
            timestamp = int(re.search(regexPattern1, bodyResponse).group(1))
            dtObject = datetime.fromtimestamp(timestamp)
            encryptionType = "RSA 2048-bit (Older but faster)"
        except:
            try:
                timestamp = int(re.search(regexPattern2, bodyResponse).group(1))
                dtObject = datetime.fromtimestamp(timestamp)
                encryptionType = "RSA 4096-bit (Secure but slow)"
            except:
                timestamp = int(re.search(regexPattern3, bodyResponse).group(1))
                dtObject = datetime.fromtimestamp(timestamp)
                encryptionType = "X25519 (Modern, fastest, secure)"

        pubKey = httpx.get(f'https://api.protonmail.ch/pks/lookup?op=get&search={email}')
        pgpKey = pubKey.text

        output = {
            'Created': dtObject,
            'PGP Encryption Type': encryptionType,
            'PGP Key': pgpKey
        }

        PrintUtil.prettify(output)

    @classmethod
    def check(cls):
        return True  # Replace with actual check logic
