import re
from pathlib import Path, PosixPath
from typing import Union, Any, Generator, Tuple

from igit.util.misc import darkprint, yellowprint
from igit.util.regex import FILE_SUFFIX, is_only_regex, has_glob, is_only_glob


class ExPath(PosixPath):
    
    def __new__(cls, *paths, **kwargs):
        if not paths or any(not seg for seg in paths):
            raise ValueError(f"ExPath.__new__(paths): bad paths: {paths}")
        return super().__new__(cls, *paths, **kwargs)
    
    def __contains__(self, other):
        return other in str(self)
    
    def __getattribute__(self, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            if hasattr(str, name):
                ret = str(self).__getattribute__(name)
                return ret
            raise
    
    def __eq__(self, other) -> bool:
        return Path(self) == Path(other)
    
    # def __eq__(self, other):
    #     darkprint(f'{repr(self)}.__eq__(other={repr(other)})')
    #     try:
    #         return self.samefile(other)
    #     except FileNotFoundError as e:
    #         darkprint(f'{repr(self)}.__eq__(other={repr(other)}) FileNotFoundError')
    #         return self.samefile(other.absolute())
    #         # try:
    #         # except AttributeError:
    #         #     raise e
    #     except Exception as e:
    #         cprint(ExcHandler(e).short(other), 'yellow')
    #         return Path(self) == Path(other)
    
    def __hash__(self) -> int:
        return super().__hash__()
    
    def has_glob(self) -> bool:
        return has_glob(str(self))
    
    def _partition_parts_by_glob(self) -> Tuple[str, str, str]:
        """
        >>> ExPath('/usr/local/*/man')._partition_parts_by_glob()
        ('/usr/local', '*', 'man')
        >>> ExPath('/usr/local/share/man')._partition_parts_by_glob()
        ('/usr/local/share/man', '', '')
        >>> ExPath('*.d.ts')._partition_parts_by_glob()
        ('*.d.ts', '', '')
        """
        if len(self.parts) <= 1:
            return str(self), '', ''
        parts_before_glob = []
        parts_after_glob = []
        globpart = ''
        for i, part in enumerate(self.parts):
            if has_glob(part):
                globpart = part
                parts_after_glob = self.parts[i + 1:]
                break
            parts_before_glob.append(part)
        if parts_before_glob and parts_before_glob[0] == '/':
            # avoid joining '/', 'usr' → '//usr'
            return '/' + '/'.join(parts_before_glob[1:]), globpart, '/'.join(parts_after_glob)
        return '/'.join(parts_before_glob), globpart, '/'.join(parts_after_glob)
    
    def glob(self, pattern: str = None) -> Generator['ExPath', None, None]:
        """Like vanilla `.glob()` but supports passing no arguments if self contains a globbing pattern.
        Yields dirs and files.
        >>> ExPath('/usr/*').glob()
        <generator object ExPath.glob at 0x...>
        >>> ExPath('*.d.ts').glob()
        <generator object ExPath.glob at 0x...>
        """
        if pattern is None:
            if not self.has_glob():
                raise TypeError(f"glob() with no arguments is only possible if self contains a globbing pattern")
            if len(self.parts) > 1:
                parts_before_glob, glob_part, parts_after_glob = self._partition_parts_by_glob()
                globgen = ExPath(parts_before_glob).glob('/'.join([glob_part, parts_after_glob]))
            else:
                # *.d.ts
                globgen = ExPath('.').glob(str(self))
            
            yield from globgen
            # self_string = str(self)
            # before_star, star, after_star = self_string.partition('*')
            # yield from ExPath(before_star).glob(f'{star}{after_star}')
        else:
            yield from super().glob(pattern)
    
    def is_dir(self) -> bool:
        """Has to exist and be a directory"""
        is_dir = super().is_dir()
        if is_dir:
            return True
        if has_file_suffix(self):
            return False
        if not self.exists():
            return False
        if self.has_glob():
            glob_parts_idxs = [i for i, part in enumerate(self.parts) if has_glob(part)]
            if len(glob_parts_idxs) > 1:
                raise NotImplementedError
                # TODO (CONTINUE): resume here:
                #  https://www.notion.so/Journal-a754564aceed42668474e6446c8028c3#08be0130d0744a57abcd5737587d7dc7
                # noinspection PyUnreachableCode
                concrete_paths = []
                for i, glob_idx in enumerate(glob_parts_idxs):
                    try:
                        tmp_path = ExPath(*self.parts[:glob_parts_idxs[i + 1]])
                        if tmp_path.is_dir():
                            concrete = next(tmp_path.glob())
                            concrete_paths.append(concrete)
                        else:
                            return False
                    except IndexError:
                        ...
            parts_before_glob, glob_part, parts_after_glob = self._partition_parts_by_glob()
            if is_only_glob(glob_part):
                # e.g. '.../*/...'
                if not parts_after_glob:
                    # e.g. '/home/*'
                    return ExPath(parts_before_glob).is_dir()
                # prev_parts = []
                # for i, part in enumerate(self.parts):
                #     if has_glob(part):
                #         if is_only_glob(part):
                #             if ExPath(*prev_parts).is_dir():
                #                 current_path = ExPath(*prev_parts, part)
                #                 concrete_path = next(current_path.glob())
                #                 prev_parts.append(concrete_path.stem)
                #             else:
                #                 return False
                #         else:
                #             current_path = ExPath(*prev_parts, part)
                #             if current_path.is_dir():
                #                 concrete_path = next(current_path.glob())
                #                 prev_parts.append(concrete_path.stem)
                #             else:
                #                 return False
                #     else:
                #         prev_parts.append(part)
            return all([subpath.is_dir() for subpath in self.glob()])
            #     if has_glob(parts_after_glob):
            #         # either '/home/*/.b*shrc' or 'home/*/D*wnloads'
            #     # either '/home/*/.bashrc' or 'home/*/Downloads'
            #     return all([subpath.is_dir() for subpath in self.glob()])
            # # e.g. '.../f*obar/...'
            # return all([subpath.is_dir() for subpath in self.glob()])
        
        self_string = str(self)
        if '*' in self_string:
            if self_string.endswith('*'):
                # e.g. 'some_path*', 'some_path/*', ...
                before_star, *_ = self_string.partition('*')
                try:
                    return ExPath(before_star).is_dir()
                except ValueError as e:
                    if any('bad paths' in arg for arg in e.args):  # __new__()
                        return False
                    raise
            # e.g. '*.foo', 'some_*/', ...
            # TODO: this is a partial solution
            before_star, star, after_star = self_string.partition('*')
            if '/' not in after_star:
                # *.py[cod] is a file, not a dir
                return False
            return self.exists()  # TODO: maybe just super().exists()
        else:
            return False
    
    def is_file(self) -> bool:
        """Has to exist and be a file.
        If self is glob, all resulting paths must be a file"""
        if super().is_file():
            return True
        if not self.exists():
            return False
        # parts_before_glob, glob_part, parts_after_glob = self._partition_parts_by_glob()
        
        try:
            for subpath in self.glob():
                if not subpath.is_file():
                    return False
            return True
        except TypeError:
            return False
    
    def exists(self) -> bool:
        if super().exists():
            return True
        try:
            # maybe self has globbing, in which case return True if globbing yields anything
            # (vanilla globbing yields only existing paths)
            return bool(list(self.glob()))
        except TypeError as e:
            return False
    
    def regex(self, pattern, predicate=bool) -> Generator['ExPath', None, None]:
        """Like Path.glob(), but supports full python regex"""
        for item in list(filter(predicate, self.iterdir())):  # todo: remove list when done debugging
            if item.is_dir():
                yield from item.regex(pattern, predicate)
            elif re.match(pattern, str(item)):
                yield item
        return
    
    def subpath_of(self, other: 'ExPathOrStr'):
        return ExPath(other).parent_of(self)
    
    def parent_of(self, other: 'ExPathOrStr'):
        """
         Both have to exist. Parent has to be a dir, subpath can also be a file.
         '/usr/*' is considered a parent of '/usr/local'.
        >>> ExPath('/usr').parent_of('/usr/local')
        True
        >>> subpaths = ['/usr/local', '/usr/local/bin','/usr/local/*', '/usr/*/bin']
        >>> all(ExPath('/usr/*').parent_of(subpath) for subpath in subpaths)
        True
        >>> all(not ExPath('/usr/BAD').parent_of(subpath) for subpath in subpaths)
        True
        >>> all(not ExPath('/usr/*/BAD').parent_of(subpath) for subpath in subpaths)
        True
        """
        if not self.is_dir():
            return False
        other = ExPath(other)
        if not other.exists():
            return False
        if self == other:
            return False
        if self.has_glob():
            for path in self.glob():
                if path == other:
                    # ('/usr/*').parent_of('/usr/bin') is True
                    return True
                if path.parent_of(other):
                    return True
        if other.has_glob():
            if other.parts[-1] == '*':
                # '/usr' isn't parent of '/usr/*'
                return self.parent_of(ExPath(*other.parts[:-1]))
            # ALL subpaths of other need to be subpath of self
            # (is this necessary? maybe one is enough?)
            for path in other.glob():
                if not self.parent_of(path):
                    return False
            return True
        
        self_string = str(self)
        other_string = str(other)
        # if '*' in self_string:
        #     if not self_string.endswith('*'):
        #         raise NotImplementedError(f"self has `*` but not in the end. self: {self}", self)
        #     self_before, *_ = self_string.partition('*')
        #     if not self_before.endswith('/'):
        #         raise NotImplementedError(f"self has `*` but not preceded by '/'. self: {self}", self)
        #     if '*' in other_string:
        #         other_before, *_ = other_string.partition('*')
        #         return ExPath(self_before).parent_of(other_before)
        #     return ExPath(self_before).parent_of(other)
        try:
            return other_string.startswith(self_string)
        except ValueError:
            return False


# ExPath = Path
# ExPath.__contains__ = __contains__
# ExPath.subpath_of = subpath_of
# ExPath.parent_of = parent_of


ExPathOrStr = Union[str, ExPath]


def dirsize(path: ExPathOrStr) -> int:
    """Returns size in bytes"""
    if isinstance(path, str):
        return dirsize(Path(path))
    return sum(f.lstat().st_size for f in path.glob('**/*') if f.is_file())


def has_file_suffix(path: ExPathOrStr) -> bool:
    """Returns True when detects file suffix, e.g. '.*/my_weird-file*v.d?.[ts]' (or 'file.txt').
    Returns False in cases like '.*/py_venv.*/' (or 'file')
    >>> all(map(has_file_suffix, ['.*/my_weird-file*v.d?.[ts]', 'file.txt']))
    True
    >>> any(map(has_file_suffix, ['.*/py_venv.*/', 'file']))
    False
    """
    path = ExPath(path)
    if '.' not in str(path):
        return False
    
    suffixes = path.suffixes
    # path = Path(path)
    # suffix = path.suffix
    if not suffixes:
        return False
    # stem, *_ = path.partition('.')
    # stem = path.stem
    is_stem_only_regex = is_only_regex(path.stem)
    if is_stem_only_regex:
        # something like "*.mp4" returns True
        return any(bool(re.fullmatch(FILE_SUFFIX, '.' + suffix)) for suffix in suffixes)  # nice suffix
    
    else:
        any_suffix_has_non_regex = any(not is_only_regex(suffix) for suffix in suffixes)
        if any_suffix_has_non_regex:
            return True
    return False


def has_file_suffixOLD(path: ExPathOrStr) -> bool:
    """Returns True when detects file suffix, e.g. '.*/my_weird-file*v.d?.[ts]' (or 'file.txt').
    Returns False in cases like '.*/py_venv.*/' (or 'file')
    >>> all(map(has_file_suffix, ['.*/my_weird-file*v.d?.[ts]', 'file.txt']))
    True
    >>> any(map(has_file_suffix, ['.*/py_venv.*/', 'file']))
    False
    """
    path = str(path)
    if '.' not in path:
        return False
    suffixes = [split for split in path.split('.')[1:] if split]
    # path = Path(path)
    # suffix = path.suffix
    if not suffixes:
        return False
    stem, *_ = path.partition('.')
    # stem = path.stem
    is_stem_only_regex = is_only_regex(stem)
    if is_stem_only_regex:
        # something like "*.mp4" returns True
        return any(bool(re.fullmatch(FILE_SUFFIX, '.' + suffix)) for suffix in suffixes)  # nice suffix
    
    else:
        any_suffix_has_non_regex = any(not is_only_regex(suffix) for suffix in suffixes)
        if any_suffix_has_non_regex:
            return True
    return False
