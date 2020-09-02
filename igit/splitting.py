from igit.expath import ExPathOrStr, ExPath


def splitfile(file: ExPathOrStr) -> ExPath:
    split_prefix = abspath.with_name(abspath.stem + f'_{abspath.suffix[1:]}_').with_suffix('')
