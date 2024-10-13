import os
import random
import subprocess

from .logger import Logger

class ConsoleUtil:
    VERSION = '0.0.1'

    BANNER = '''
    \x1b[96m   ____       __              
    \x1b[96m  / __ \\___  / /____ ___  ___ 
    \x1b[96m / /_/ / _ \\/ __/ -_) _ `/ _ \\
    \x1b[96m \\____/ .__/\\__/\\__/\\_, /\\___/
    \x1b[96m     /_/           /___/ \x1b[0mv %(VERSION)s
    ''' 

    @staticmethod
    def clear_screen():
        """ Clear console screen """
        subprocess.call('cls' if os.name == 'nt' else 'clear', shell=True)

    @staticmethod
    def set_title(title: str):
        """ Set console title """
        if os.name == 'nt':
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        else:
            print('\x1b]0;' + title, end='\a')

    @staticmethod
    def yn_prompt(prompt: str) -> bool:
        """ Spawn Yes/No prompt """
        while True:
            answer = input(prompt)
            
            if len(answer) == 0:
                continue

            answer = answer.lower()

            if answer.startswith('y'):
                return True

            elif answer.startswith('n'):
                return False

            Logger.warning('Input must be either Yes or No')

    @staticmethod
    def print_banner():
        """ Print banner """
        print(ConsoleUtil.BANNER.lstrip(' ').replace('##', random.choice('8o.-_#|@0!/\\?+><*`´¨') * 2) % {'VERSION': ConsoleUtil.VERSION} + '\x1b[0m')
