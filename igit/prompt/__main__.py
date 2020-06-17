# for debugging, i.e. python -m igit.prompt 'whatever'
import sys
import click
from typing import Tuple
from igit.util.clickextensions import unrequired_opt


@click.command()
@click.argument('fnname')
@click.argument('options', nargs=-1)
@unrequired_opt('--free-input', is_flag=True)
def main(fnname, options, free_input):
    print(f'fnname: {fnname}',
          f'options: {repr(options)}',
          f'free_input: {free_input}',
          sep='\n')
    from . import prompt
    fn = getattr(prompt, fnname)
    print(f'fn: {fn}')
    ret = fn(*options, free_input=free_input, flowopts='continue')
    print(f'ret: {repr(ret)}')


if __name__ == '__main__' and len(sys.argv) > 1:
    main()
