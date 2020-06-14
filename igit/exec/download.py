import os

from more_termcolor import colors
import requests
import click

ALIASES = ['down', 'download', 'dl']

USAGE = f"""download {colors.italic('<remote> <dest> <file> [<*files...>]', False)}
        <remote>: {colors.italic('reponame[@branchname]', False)}
        aliases: {ALIASES}"""


@click.command()
@click.command()
def main(_remote: str, _branch: str, _dest: str, _files: [str]):
    for _file in _files:
        print(f'\ndownloading {_file}...')
        savepath = os.path.join(_dest, _file)
        overwrite = False
        if os.path.exists(savepath):
            answer = input(f'{savepath} exists ({os.path.getsize(savepath)}B). overwrite? y/n\t')
            if answer.lower() == 'y':
                overwrite = True
            else:
                print(f'skipping {_file}')
                return
        url = f'https://raw.githubusercontent.com/{_remote}/{_branch}/{_file}'
        req = requests.get(url)
        while not req.ok and '/' in _remote:
            _remote, _, _subdir = _remote.rpartition('/')
            err_msg = f'Couldnt download {_file}. status_code: {req.status_code}. url: {url}. Maybe {_subdir} is a subdir? Trying...'
            print(colors.yellow(err_msg))
            url = f'https://raw.githubusercontent.com/{_remote}/{_branch}/{_subdir}/{_file}'
            req = requests.get(url)
        else:
            util.exitif('/' not in _remote, (f'Couldnt download {_file}. status_code: {req.status_code}. url: {url}\n'
                                             f'        {dict(_remote=_remote, _branch=_branch, _file=_file)}'))
        
        with open(savepath, mode="wb" if overwrite else "xb") as f:
            try:
                f.write(req.content.decode())
            except UnicodeDecodeError as ude:
                print(colors.yellow(f'Caught a UnicodeDecodeError when trying to {colors.italic("req.content.decode()")}'))
                f.write(req.content)
        
        print(colors.green(f'Successfully downloaded {_file} to {savepath}.'))
        if overwrite:
            print(f'new file size: {os.path.getsize(savepath)}')


if __name__ == '__main__':
    main()
