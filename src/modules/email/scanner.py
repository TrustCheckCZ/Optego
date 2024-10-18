import trio
import httpx
import pkgutil
import importlib
from cli import PrintUtil, Logger
from plugins import Plugin, register_plugin

@register_plugin
class SiteScan(Plugin):
    plugin_type = 'email'

    def run(self, target):
        def import_submodules(package, recursive=True):
            results = {}

            if isinstance(package, str):
                package = importlib.import_module(package)

            for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
                full_name = package.__name__ + "." + name
                results[full_name] = importlib.import_module(full_name)

                if recursive and is_pkg:
                    results |= import_submodules(full_name)

            return results

        def get_functions(modules, args=None):
            websites = []

            for module in modules:
                if len(module.split(".")) > 3:
                    modu = modules[module]
                    site = module.split(".")[-1]
                    websites.append(modu.__dict__[site])

            return websites

        async def launch_module(module, email, client, out):
            data = {
                "aboutme": "about.me",
                "adobe": "adobe.com",
                "amazon": "amazon.com",
                "anydo": "any.do",
                "archive": "archive.org",
                "armurerieauxerre": "armurerie-auxerre.com",
                "atlassian": "atlassian.com",
                "babeshows": "babeshows.co.uk",
                "badeggsonline": "badeggsonline.com",
                "biosmods": "bios-mods.com",
                "biotechnologyforums": "biotechnologyforums.com",
                "bitmoji": "bitmoji.com",
                "blablacar": "blablacar.com",
                "blackworldforum": "blackworldforum.com",
                "blip": "blip.fm",
                "blitzortung": "forum.blitzortung.org",
                "bluegrassrivals": "bluegrassrivals.com",
                "bodybuilding": "bodybuilding.com",
                "buymeacoffee": "buymeacoffee.com",
                "cambridgemt": "discussion.cambridge-mt.com",
                "caringbridge": "caringbridge.org",
                "chinaphonearena": "chinaphonearena.com",
                "clashfarmer": "clashfarmer.com",
                "codecademy": "codecademy.com",
                "codeigniter": "forum.codeigniter.com",
                "codepen": "codepen.io",
                "coroflot": "coroflot.com",
                "cpaelites": "cpaelites.com",
                "cpahero": "cpahero.com",
                "cracked_to": "cracked.to",
                "crevado": "crevado.com",
                "deliveroo": "deliveroo.com",
                "demonforums": "demonforums.net",
                "devrant": "devrant.com",
                "diigo": "diigo.com",
                "discord": "discord.com",
                "docker": "docker.com",
                "dominosfr": "dominos.fr",
                "ebay": "ebay.com",
                "ello": "ello.co",
                "envato": "envato.com",
                "eventbrite": "eventbrite.com",
                "evernote": "evernote.com",
                "fanpop": "fanpop.com",
                "firefox": "firefox.com",
                "flickr": "flickr.com",
                "freelancer": "freelancer.com",
                "freiberg": "drachenhort.user.stunet.tu-freiberg.de",
                "garmin": "garmin.com",
                "github": "github.com/username",
                "google": "google.com",
                "gravatar": "gravatar.com",
                "imgur": "imgur.com",
                "instagram": "instagram.com/username",
                "issuu": "issuu.com",
                "koditv": "forum.kodi.tv",
                "komoot": "komoot.com",
                "laposte": "laposte.fr",
                "lastfm": "last.fm",
                "lastpass": "lastpass.com",
                "mail_ru": "mail.ru",
                "mybb": "community.mybb.com",
                "myspace": "myspace.com",
                "nattyornot": "nattyornotforum.nattyornot.com",
                "naturabuy": "naturabuy.fr",
                "ndemiccreations": "forum.ndemiccreations.com",
                "nextpvr": "forums.nextpvr.com",
                "nike": "nike.com",
                "odampublishing": "forum.odampublishing.com",
                "odnoklassniki": "ok.ru",
                "office365": "office365.com",
                "onlinesequencer": "onlinesequencer.net",
                "parler": "parler.com",
                "patreon": "patreon.com",
                "pinterest": "pinterest.com/username",
                "plurk": "plurk.com",
                "pornhub": "pornhub.com/users/username",
                "protonmail": "protonmail.ch",
                "quora": "quora.com",
                "raidforums": "raidforums.com/user-username",
                "rambler": "rambler.ru",
                "redtube": "redtube.com",
                "replit": "repl.it/@username",
                "rocketreach": "rocketreach.co",
                "samsung": "samsung.com",
                "seoclerks": "seoclerks.com",
                "sevencups": "7cups.com",
                "smule": "smule.com",
                "snapchat": "snapchat.com/add/username",
                "sporcle": "sporcle.com",
                "spotify": "spotify.com/user/username",
                "strava": "strava.com",
                "taringa": "taringa.net",
                "teamtreehouse": "teamtreehouse.com",
                "tellonym": "tellonym.me",
                "thecardboard": "thecardboard.org",
                "therianguide": "forums.therian-guide.com",
                "thevapingforum": "thevapingforum.com",
                "treasureclassifieds": "forum.treasureclassifieds.com",
                "tumblr": "tumblr.com",
                "tunefind": "tunefind.com",
                "twitter": "twitter.com/username",
                "venmo": "venmo.com",
                "vivino": "vivino.com",
                "voxmedia": "voxmedia.com",
                "vrbo": "vrbo.com",
                "vsco": "vsco.co",
                "wattpad": "wattpad.com",
                "wordpress": "wordpress",
                "xing": "xing.com",
                "xvideos": "xvideos.com",
                "yahoo": "yahoo.com",
            }

            try:
                await module(email, client, out)
            except:
                name = str(module).split("<function ")[1].split(" ")[0]

                domain = data.get(name, "unknown domain")
                out.append(
                    {"name": name, "domain": domain, "emailrecovery": None, "exists": False}
                )

        def print_result(data, email, websites):
            account_count = 0
            accounts = []

            for account in data:
                output = {}

                if account.get('exists', False):
                    account_count += 1
                    output['Domain'] = f"http://{account.get('domain')}"

                    if account.get('emailrecovery'):
                        output['Recovery Email'] = account.get('emailrecovery')
                    
                    if account.get('phoneNumber'):
                        output['Recovery Phone'] = account.get('phoneNumber')
                    
                    if account.get('other'):
                        output['Website Data'] = account.get('other')

                    accounts.append(output)

            if account_count > 0:
                Logger.info(f'Found {account_count} registered accounts')
                PrintUtil.prettify(accounts)

                return accounts
                
        async def main(email):
            modules = import_submodules("holehe.modules")
            websites = get_functions(modules, email)

            out = []
            client = httpx.AsyncClient()

            async with trio.open_nursery() as nursery:
                for website in websites:
                    nursery.start_soon(launch_module, website, email, client, out)

            out = sorted(out, key=lambda i: i["name"])
            await client.aclose()
            print_result(out, email, websites)

        trio.run(main, target)

    @classmethod
    def check(cls):
        return True  # Replace with actual check logic
