import os
import re
from pathlib import PosixPath, Path, PurePath
from typing import Any, Tuple, Generator, Union, List, Literal, NoReturn

from igit import regex, shell
# from igit.util.path import has_file_suffix
from igit.regex import has_glob, is_only_glob
from igit_debug.loggr import Loggr

logger = Loggr()


# TODO: what happens if multi inherit str?
class ExPath(PosixPath):
    splits: List['ExPath']
    
    def __new__(cls, *paths, **kwargs):
        if not paths or any(not seg for seg in paths):
            raise ValueError(f"ExPath.__new__(paths): bad paths: {paths}")
        return super().__new__(cls, *paths, **kwargs)
    
    def __init__(self, *pathsegments: str) -> None:
        """
        >>> ExPath(__file__)._split_prefix
        'expath_py_'
        >>> ExPath('/does/not.exist')._split_prefix
        Traceback (most recent call last):
            ...
        AttributeError
        """
        super().__init__()
        
        if self.is_file():
            # file.zip → file_zip_
            # note: this means it has to exist
            _split_prefix = self.deepstem + ''.join([s.replace('.', '_') for s in self.suffixes]) + '_'
            self._split_prefix: str = _split_prefix
    
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
        try:
            return Path(self) == Path(other)
        except TypeError as e:
            # example: other is None
            return False
    
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
    
    def __truediv__(self: 'ExPath', key: Union[str, PurePath]) -> 'ExPath':
        """Both __truediv__ and __rtruediv__ are necessary because super() doesn't really
        (at all?) call __init__, so returning value is ExPath but doesn't have _split_prefix attr"""
        divved = super().__truediv__(key)
        return ExPath(divved)
    
    def __rtruediv__(self: 'ExPath', key: Union[str, PurePath]) -> 'ExPath':
        rdivved = super().__rtruediv__(key)
        return ExPath(rdivved)
    
    def splits_integrity_ok(self) -> bool:
        """Removes the joined file after joining only if integrity is ok."""
        existing_splits = self.getsplits()
        if not existing_splits:
            raise FileNotFoundError(f"ExPath.verify_splits_integrity() was called for {self}, but existing_splits were not found by split prefix: {self._split_prefix}")
        # todo: this doesn't work with shell.run for some reason
        os.system(f'cat "{self._split_prefix}"* > /tmp/joined')
        try:
            # diff returns 0 only if there's no difference
            shell.run(f'diff /tmp/joined "{self}"', raise_on_non_zero='short')
        except ChildProcessError:
            return False
        else:
            shell.run('rm /tmp/joined', raise_on_non_zero=True)
            return True
    
    def split(self, verify_integrity=False) -> List['ExPath']:
        """If verify_integrity is `True`, and splits are bad, raises OSError"""
        existing_splits = self.getsplits()
        if existing_splits:
            raise FileExistsError(f"ExPath.split() was called for {self}, but existing_splits were found:\n\t{existing_splits}")
        shell.run(f'split -d --bytes 49000KB "{self}" "{self._split_prefix}"')
        splits = self.getsplits()
        if not verify_integrity:
            return splits
        splits_ok = self.splits_integrity_ok()
        if not splits_ok:
            raise OSError(f"ExPath.split() was called for {self} with verify_integrity=True. splits are bad.")
        return splits
    
    def unsplit(self) -> NoReturn:
        existing_splits = self.getsplits()
        if not existing_splits:
            raise FileNotFoundError(f"{self}.unsplit() was called for {self}, but existing_splits were not found by split prefix: {self._split_prefix}")
    
    def getsplits(self) -> List['ExPath']:
        # TODO: make sure self.parent.glob works if self is relative
        # looks like it's fine even when stem has spaces (no need to quote)
        return list(self.parent.glob(self._split_prefix + "*"))
    
    @property
    def deepstem(self) -> str:
        """The final path component, minus ALL suffixes.
        >>> expaths = [ExPath('file'), ExPath('file.txt'), ExPath('file.txt.ignore')]
        >>> all(expath.deepstem == 'file' for expath in expaths)
        True
        >>> ExPath('/home/gilad').deepstem
        'gilad'
        >>> ExPath('/home/gilad').deepstem == Path('/home/gilad').stem
        True
        >>> ExPath('/home/gilad/foo.bar.baz').deepstem
        'foo'
        """
        
        stem = self.stem
        for suffix in self.suffixes:
            stem = stem.replace(suffix, '')
        return stem
    
    def trash(self):
        shell.run(f'gio trash "{self}"')
    
    def size(self, unit: Union[Literal['kb'], Literal['mb'], Literal['gb']] = None):
        """By default, returns size in bytes."""
        syze = self.lstat().st_size
        if not unit:
            return syze
        if unit == 'kb':
            return syze / 1000
        if unit == 'mb':
            return syze / 1000000
        if unit == 'gb':
            return syze / 1000000000
        raise ValueError(f"ExPath.size(unit={repr(unit)}), bad unit. self is {self}. accepting only kb, mb or gb (or None)")
    
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
        """Like vanilla `.glob()` but supports passing no arguments if `self` contains a globbing pattern.
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
        if self.has_file_suffix():
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
            # todo: maybe this is redundant because super() already checks whether exists?
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
        """Returns True if file or dir exist.
        In case self has globbing, return True if globbing yields anything
        (vanilla globbing yields only existing paths)"""
        if super().exists():
            return True
        try:
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
    
    def add_suffix(self, suffix):
        """
        >>> ExPath('hello.foo').add_suffix('.bar')
        ExPath('hello.foo.bar')
        >>> ExPath('hello').add_suffix('.bar')
        ExPath('hello.bar')
        """
        # taken from with_suffix source
        f = self._flavour
        if f.sep in suffix or f.altsep and f.altsep in suffix:
            raise ValueError("Invalid suffix %r" % (suffix,))
        if suffix and not suffix.startswith('.') or suffix == '.':
            raise ValueError("Invalid suffix %r" % (suffix))
        
        return self.with_suffix(f'{self.suffix}{suffix}')
    
    def has_file_suffix(self) -> bool:
        """Returns True when detects file suffix, e.g. '.*/my_weird-file*v.d?.[ts]' (or 'file.txt').
        Returns False in cases like '.*/py_venv.*/' (or 'file')
        >>> all(exp.has_file_suffix() for exp in  [ExPath('.*/my_weird-file*v.d?.[ts]'), ExPath('file.txt')])
        True
        >>> any(exp.has_file_suffix() for exp in [ExPath('.*/py_venv.*/'), ExPath('file')])
        False
        """
        if '.' not in str(self):
            return False
        
        # suffixes = path.suffixes
        # path = Path(path)
        # suffix = path.suffix
        if not self.suffixes:
            return False
        # stem, *_ = path.partition('.')
        # stem = path.stem
        is_stem_only_regex = regex.is_only_regex(self.stem)
        if is_stem_only_regex:
            # something like "*.mp4" returns True
            return any(bool(re.fullmatch(regex.FILE_SUFFIX, '.' + suffix)) for suffix in self.suffixes)  # nice suffix
        
        else:
            any_suffix_has_non_regex = any(not regex.is_only_regex(suffix) for suffix in self.suffixes)
            if any_suffix_has_non_regex:
                return True
        return False


# class StrPath(ExPath, str):
#     pass


# ExPath = Path


# ExPath.__contains__ = __contains__
# ExPath.subpath_of = subpath_of
# ExPath.parent_of = parent_of
ExPathOrStr = Union[str, ExPath]
