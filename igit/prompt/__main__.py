# for debugging, i.e. python -m igit.prompt 'whatever'
import sys
import click

from igit.util.clickextensions import unrequired_opt


@click.command()
@click.argument('fnname')
@click.argument('options', nargs=-1)
@unrequired_opt('--allow-free-input', is_flag=True)
def main(fnname, options, allow_free_input):
    from . import prompt
    fn = getattr(prompt, fnname)
    ret = fn(*options, allow_free_input=allow_free_input)
    print(f'fnname: {fnname}', f'options: {options}', f'fn: {fn}', f'ret: {ret}', sep='\n')


if __name__ == '__main__' and len(sys.argv) > 1:
    main()
