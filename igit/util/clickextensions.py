import click


def option(*param_decls, **attrs):
    """show_default=True.
    If 'default' in attrs, sets `type` (and vice versa)"""
    attrs['show_default'] = True
    default = attrs.get('default', click.core._missing)
    default_is_missing = default is click.core._missing
    if default_is_missing:
        typeattr = attrs.get('type', click.core._missing)
        if not (typeattr is click.core._missing):
            attrs['type'] = typeattr
            attrs['default'] = typeattr()
    else:
        attrs['type'] = type(default)
    
    return click.option(*param_decls, **attrs)


def unrequired_opt(*param_decls, **attrs):
    """show_default=True, required=False.
    If 'default' in attrs, sets `type` (and vice versa)"""
    attrs['required'] = False
    return option(*param_decls, **attrs)


def required_opt(*param_decls, **attrs):
    """show_default=True, required=True.
        If 'default' in attrs, sets `type` (and vice versa)"""
    attrs['required'] = True
    return option(*param_decls, **attrs)
