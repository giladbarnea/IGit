import os

import re

from more_termcolor import cprint


def clip_copy(text: str):
    stripped = text.strip()
    assert '\n' not in stripped
    os.system(f'echo {stripped} | xclip -r -selection clipboard')


def unquote(string) -> str:
    # TODO: "gallery is MOBILE only if <= $BP3" -> "gallery is MOBILE only if <=" (maybe bcz bash?)
    string = str(string)
    match = re.fullmatch(r'(["\'])(.*)\1', string, re.DOTALL)
    if match:  # "'hello'"
        string = match.groups()[1]
    return string.strip()


def quote(string) -> str:
    if '"' in string:
        if "'" in string:
            raise NotImplementedError(f"quote() got string with both types of quotes, escaping not impl", string)
        return f"'{string}'"
    elif "'" in string:
        if '"' in string:
            raise NotImplementedError(f"quote() got string with both types of quotes, escaping not impl", string)
        return f'"{string}"'
    return f'"{string}"'


def trim_at(string: str, idx: int) -> str:
    if len(string) > idx:
        return f'{string[:idx - 3]}...'
    return string


def is_pycharm():
    is_pycharm = 'JetBrains/Toolbox/apps/PyCharm-P' in os.environ.get('PYTHONPATH', '')
    if is_pycharm:
        print('pycharm!')
    return is_pycharm


def getsecret(label: str) -> str:
    import secretstorage
    con = secretstorage.dbus_init()
    col = secretstorage.get_default_collection(con)
    secret = None
    for item in col.get_all_items():
        if item.get_label() == label:
            return item.get_secret().decode()


def try_convert_to_slice(val: str) -> slice:
    """Returns either slice or as-is if conversion fails"""
    try:
        val = val.strip()
        if val.isdigit():
            stop = int(val) + 1
            return slice(stop)
        if ':' in val:
            start, _, stop = val.partition(':')
            return slice(int(start), int(stop))
        return val
    except AttributeError as e:  # AttributeError: 'slice' object has no attribute 'strip'
        return val


def try_convert_to_idx(val: str) -> int:
    """Returns either int or as-is if conversion fails"""
    try:
        val = val.strip()
        if val.isdigit():
            return int(val)
        if ':' in val:
            raise ValueError(f"':' in val: {val}. Use try_convert_to_slice()")
        return val
    except AttributeError as e:
        return val


def darkprint(string):
    cprint(string, 'dark')


def greenprint(string):
    cprint(string, 'green')


def yellowprint(string):
    cprint(string, 'yellow')


def brightyellowprint(string):
    cprint(string, 'bright yellow')


def brightredprint(string):
    cprint(string, 'bright red')
