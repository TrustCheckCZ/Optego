from .logger import Logger

class PrintUtil:
    @staticmethod
    def _prettify_dict(_dict: dict) -> dict:
        """ Prettify dictionary """
        max_key_len = 0

        for key in _dict.keys():
            if len(key) > max_key_len:
                max_key_len = len(key)

        result = {}

        for key, value in _dict.items():
            # Replace underscores with spaces and capitalize each new word
            key = key.replace('_', ' ').title()
            key += '.' * (max_key_len - len(key))
            result |= {key: value}

        return result

    @staticmethod
    def _prettify_bool(_bool: bool) -> str:
        return 'Yes' if _bool is True else 'No'

    @classmethod
    def prettify(cls, results):
        if not isinstance(results, list) and not isinstance(results, tuple):
            if not isinstance(results, dict):
                raise Exception('First parameter in PrintUtil.pp() must be an iterable')

            if not results:
                raise Exception('No information found')

            results = [results]

        if not results:
            raise Exception('No information found')

        for i, result in enumerate(results):
            result = cls._prettify_dict(result)

            for k, v in result.items():
                if v is None:
                    continue

                color_code = 90

                if isinstance(v, list):
                    if len(v) == 0:
                        continue

                    print(f'\x1b[92m•\x1b[0m {k}:\x1b[0m')

                    dots = '.' * len(list(result.keys())[0])

                    sample_value = v[0]

                    if isinstance(sample_value, list):
                        max_len = 0
                        for x in [x for x in v if x]:
                            if len(x[0]) > max_len:
                                max_len = len(x[0])

                    elif isinstance(sample_value, dict):
                        max_elem_lens = {}

                        for x in [x for x in v if x]:
                            for j, v1 in enumerate(x.values()):
                                if max_elem_lens.get(j) is None:
                                    max_elem_lens[j] = 0

                                if len(str(v1)) > max_elem_lens[j]:
                                    max_elem_lens[j] = len(str(v1))

                    for i1, x in enumerate([x for x in v if x]):
                        if isinstance(x, list):
                            spaces = ' ' * (max_len - len(x[0]))
                            print(f'\x1b[0m..{dots}: \x1b[90m{x[0]} {spaces}\x1b[94m({x[1]})\x1b[0m')

                        elif isinstance(x, dict):
                            itm = ' \x1b[97m│\x1b[0m '.join(f'\x1b[97m{k1 + ":" if i1 == 0 else " " * (len(k1) + 1)} \x1b[90m{v1}\x1b[0m' + (' ' * (max_elem_lens[j] - len(str(v1)))) for j, (k1, v1) in enumerate(x.items()))
                            print(f'\x1b[0m..{dots}: \x1b[90m{itm}\x1b[0m')

                        else:
                            print(f'\x1b[0m..{dots}: \x1b[90m{x}\x1b[0m')

                    continue

                elif isinstance(v, str):
                    # v = v.replace('\n', '\n')
                    if '\n' in v:
                        v = '\n' + v

                    if len(v.strip().strip(' ')) == 0:
                        continue

                elif isinstance(v, bool):
                    color_code = 92 if v else 91
                    v = cls._prettify_bool(v)

                elif isinstance(v, (int, float)):
                    color_code = 93

                if isinstance(v, dict):
                    print(f'\x1b[92m•\x1b[0m {k}: \x1b[90m{v}\x1b[0m')
                    continue

                print(f'\x1b[92m•\x1b[0m {k}: \x1b[{color_code}m{v}\x1b[0m')

            # if i < len(results) - 1:
            #     Logger.nl()
