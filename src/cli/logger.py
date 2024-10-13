import sys
from typing import Union

class Logger:
    @staticmethod
    def __log(color, prefix, *message, file=sys.stdout, noprint=False) -> Union[str, None]:
        message = ' '.join(list(map(str, message)))

        final = f'{color}{prefix}\x1b[0m {message}\x1b[0m'

        if noprint is True: return final

        print(final, file=file)

    @classmethod
    def success(cls, *message, noprint: bool = False) -> Union[str, None]:
        return cls.__log('\x1b[92m', '•', *message, noprint=noprint)

    @classmethod
    def info(cls, *message, noprint: bool = False) -> Union[str, None]:
        return cls.__log('\x1b[94m', '•', *message, noprint=noprint)

    @classmethod
    def warning(cls, *message, noprint: bool = False) -> Union[str, None]:
        return cls.__log('\x1b[93m', '•', *message, noprint=noprint)

    @classmethod
    def error(cls, *message, noprint: bool = False) -> Union[str, None]:
        return cls.__log('\x1b[91m', '•', *message, file=sys.stderr, noprint=noprint)

    @classmethod
    def usage(cls, *message, noprint: bool = False) -> Union[str, None]:
        return cls.__log('\x1b[95m', '•', *message, noprint=noprint)

    @staticmethod
    def nl(): 
        print()
