import click
import typing


def option(*param_decls, **attrs):
    """`show_default=True`.
    
    If `default` in `attrs` and `type` is not, or vice versa, sets one based on the other.
    
    `type` can be either:
     - `str`
     - `(str, int)`
     - `typing.Literal['foo']`
     - `click.typing.<Foo>` (which includes click.Choice(...))
    """
    attrs['show_default'] = True
    default = attrs.get('default', click.core._missing)
    default_is_missing = default is click.core._missing
    typeattr = attrs.get('type', click.core._missing)
    type_is_missing = typeattr is click.core._missing
    if not type_is_missing:
        if typing.get_origin(typeattr) is typing.Literal:
            # type=typing.Literal['foo']. build a click.Choice from it
            attrs['type'] = click.Choice(typeattr.__args__)
            if default_is_missing:
                # take first Literal arg
                attrs['default'] = typeattr.__args__[0]
            return click.option(*param_decls, **attrs)
        
        # not a typing.Literal (e.g. `str`)
        attrs['type'] = typeattr
        if default_is_missing:
            attrs['default'] = typeattr()
        return click.option(*param_decls, **attrs)
    
    # type is missing.
    if not default_is_missing:
        attrs['type'] = type(default)
        return click.option(*param_decls, **attrs)
    
    # type and default both missing. not sure if this works
    return click.option(*param_decls, **attrs)


def unrequired_opt(*param_decls, **attrs):
    attrs['required'] = False
    return option(*param_decls, **attrs)


def required_opt(*param_decls, **attrs):
    attrs['required'] = True
    return option(*param_decls, **attrs)
