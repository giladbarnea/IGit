"""-svv -c igit/tests/pytest.ini"""
import os
from pathlib import Path

import pytest

from igit.expath import ExPath
from igit.regex import REGEX_CHAR
from igit.tests.common import get_permutations_in_size_range, has_letters_and_punc, path_regexes, mixed_suffixes
from igit.util import misc

giladdirstr = os.getenv('HOME')  # /home/gilad
HOME_EXPATH = ExPath('/home')

GILAD_EXPATH = ExPath(giladdirstr)


def path_ctor_permutations(path: str):
    """Yields a `str(path)`, `Path(path)` and `ExPath(path)`"""
    for ctor in str, Path, ExPath:
        yield ctor(path)


class Test__ExPath:
    class glob:
        class exists__is_dir__is_file:
            def test__doesnt_exist__0(self):
                bad = ExPath('/uzer/*')
                assert not bad.exists()
                assert not bad.is_dir()
                assert not bad.is_file()
                
                bad2 = ExPath('/*DOESNTEXIST')
                assert not bad2.exists()
                assert not bad2.is_dir()
                assert not bad2.is_file()
            
            def test__single_wildcard__whole_part__0(self):
                assert ExPath('/usr/*').is_dir()
                assert ExPath('/usr/*/share').is_dir()
                assert ExPath('/*/local/share').is_dir()
                assert ExPath('/usr/*/BAD').is_dir() is False
                assert ExPath('/usr/*/shar').is_dir() is False
                assert ExPath('/usr/*/shar').is_file() is False
                assert ExPath('/usr/*/shar').exists() is False
                assert ExPath('/*/local/shar').is_dir() is False
                assert ExPath('/*/local/shar').is_file() is False
                assert ExPath('/*/local/shar').exists() is False
                assert ExPath('/home/gilad/*').is_dir()
                assert ExPath('/home/gilad/*').is_file() is False
                assert ExPath('/home/*/.bashrc').is_dir() is False
                assert ExPath('/home/*/.bashrc').is_file()
                assert ExPath('/*/gilad/.bashrc').is_file()
            
            def test__single_wildcard__whole_part__1(self):
                assert ExPath('/*/gilad').is_dir()
                assert ExPath('/*/gilad').is_file() is False
            
            def test__single_wildcard__part_of_part(self):
                assert ExPath('/home/gilad/.bashr*').is_file()
                assert ExPath('/home/gil*d').is_dir()
                assert ExPath('/home/gil*d').is_file() is False
                assert ExPath('/*ome/gilad').is_dir()
                assert ExPath('/*ome/gilad').is_file() is False
                assert ExPath('/home/gil*d/.bashrc').is_dir() is False
                assert ExPath('/home/gil*d/.bashrc').is_file()
                assert ExPath('/*ome/gilad/.bashrc').is_file()
            
            @pytest.mark.skip('Not Implemented')
            def test__multiple_wildcards__whole_part(self):
                assert ExPath('/*/gilad/*').is_dir()
                assert ExPath('/*/gilad/*').is_file() is False
            
            @pytest.mark.skip('Not Implemented')
            def test__multiple_wildcards__part_of_part(self):
                assert ExPath('/home/*/.b*shrc').is_dir() is False
                assert ExPath('/home/*/.b*shrc').is_file()
                assert ExPath('/*ome/*/.b*shrc').is_dir() is False
                assert ExPath('/*ome/*/.b*shrc').is_file()
                assert ExPath('/*/*/.b*shrc').is_file()
                assert ExPath('/*/*/.b*shrc').is_dir() is False
                assert ExPath('/home/gil*d/.b*shrc').is_dir() is False
                assert ExPath('/home/gil*d/.b*shrc').is_file()
                assert ExPath('/home/gil*d/*').is_file() is False
                assert ExPath('/home/gil*d/*').is_dir()
                assert ExPath('/*/gil*d/*').is_dir()
                assert ExPath('/*/gil*d/*').is_file() is False
            
            def test__mixed_dirs_and_files__single_wildcard(self):
                # assumes .yarn/ and .yarnrc exist
                yarn = ExPath('/home/gilad/.yarn*')
                assert yarn.exists()
                assert not yarn.is_dir()
                assert not yarn.is_file()
            
            @pytest.mark.skip('Not Implemented')
            def test__mixed_dirs_and_files__multiple_wildcards(self):
                # assumes .yarn/ and .yarnrc exist
                yarn = ExPath('/home/*/.yarn*')
                assert yarn.exists()
                assert not yarn.is_dir()
                assert not yarn.is_file()
        
        class subpath_of:
            def test__ExPath__subpath_of__wildcard(self):
                home = ExPath('/home/*')
                gilad = ExPath(giladdirstr)
                assert gilad.subpath_of(home)
                assert gilad.subpath_of('/home/')
                assert gilad.subpath_of(Path('/home'))
        
        class parent_of:
            
            class glob_subpath:
                def test__usr__0(self):
                    usr_wc = ExPath('/usr')
                    for path in path_ctor_permutations('/usr/local/*'):
                        assert usr_wc.parent_of(path)
                
                def test__usr__1(self):
                    # because '/usr/*' is parent of '/usr/local',
                    # '/usr/' isn't parent of '/usr/*'
                    # (because they function the same)
                    usr_wc = ExPath('/usr/')
                    for path in path_ctor_permutations('/usr/*'):
                        assert not usr_wc.parent_of(path)
                
                def test__usr__2(self):
                    usr_wc = ExPath('/usr/')
                    for path in path_ctor_permutations('/usr/*/share'):
                        assert usr_wc.parent_of(path)
                
                def test__usr__3(self):
                    usr_wc_share = ExPath('/usr/local/share')
                    for path in path_ctor_permutations('/usr/local/share/man/*'):
                        assert usr_wc_share.parent_of(path)
                
                def test__parent_not_exists(self):
                    usr_wc_share = ExPath('/usr/local/sherr')  # typo
                    for path in path_ctor_permutations('/usr/local/share/man/*'):
                        assert not usr_wc_share.parent_of(path)
                
                def test__neither_exist(self):
                    usr_wc_share = ExPath('/usr/local/sherr')  # typo
                    for path in path_ctor_permutations('/usr/local/sherr/man/*'):
                        assert not usr_wc_share.parent_of(path)
                
                def test__subpath_not_exists__0(self):
                    usr_wc_share = ExPath('/usr/local/share')
                    for path in path_ctor_permutations('/usr/local/share/bad'):
                        assert not usr_wc_share.parent_of(path)
                
                def test__subpath_not_exists__1(self):
                    usr_wc_share = ExPath('/usr/local/share')
                    for path in path_ctor_permutations('/usr/local/*/bad'):
                        assert not usr_wc_share.parent_of(path)
                
                def test__parent_is_actually_file(self):
                    # both really exist but a file isn't a parent of anything
                    file = ExPath('/home/gilad/.local/bin/pip')
                    for otherfile in path_ctor_permutations('/home/gilad/.local/bin/p*p3'):
                        assert not file.parent_of(otherfile)
                
                def test__subpath_is_actually_file(self):
                    file = ExPath('/home/gilad/.local/bin')
                    for otherfile in path_ctor_permutations('/home/gilad/.local/bin/p*p3'):
                        assert file.parent_of(otherfile)
                
                def test__real_world(self):
                    parent = ExPath('.idea')
                    subpath = '*.d.ts'
                    parent.parent_of(subpath)
            
            class glob_parent:
                def test__usr__0(self):
                    usr_wc = ExPath('/usr/*')
                    for path in path_ctor_permutations('/usr/local'):
                        assert usr_wc.parent_of(path)
                
                def test__usr__1(self):
                    usr_wc = ExPath('/usr/*')
                    for path in path_ctor_permutations('/usr/local/bin'):
                        assert usr_wc.parent_of(path)
                
                def test__usr__2(self):
                    usr_wc_share = ExPath('/usr/*/share')
                    for path in path_ctor_permutations('/usr/local/share/man'):
                        assert usr_wc_share.parent_of(path)
                
                def test__usr__3(self):
                    usr_wc = ExPath('/usr/*')
                    for path in path_ctor_permutations('/usr/'):
                        assert not usr_wc.parent_of(path)
                
                def test__parent_not_exists(self):
                    usr_wc_share = ExPath('/usr/*/sherr')  # typo
                    for path in path_ctor_permutations('/usr/local/share/man'):
                        assert not usr_wc_share.parent_of(path)
                
                def test__neither_exist(self):
                    usr_wc_share = ExPath('/usr/*/sherr')  # typo
                    for path in path_ctor_permutations('/usr/local/sherr/man'):
                        assert not usr_wc_share.parent_of(path)
                
                def test__subpath_not_exists__0(self):
                    usr_wc_share = ExPath('/usr/*/share')
                    for path in path_ctor_permutations('/usr/local/share/bad'):
                        assert not usr_wc_share.parent_of(path)
                
                def test__parent_is_actually_file(self):
                    # both really exist but a file isn't a parent of anything
                    file = ExPath('/home/gilad/.local/bin/pip*')
                    for otherfile in path_ctor_permutations('/home/gilad/.local/bin/pip3'):
                        try:
                            assert not file.parent_of(otherfile)
                        except AssertionError as e:
                            misc.brightredprint(f'file: {repr(file)} ({type(file)}) is not parent of otherfile: {repr(otherfile)} ({type(otherfile)})')
                            raise
                
                @pytest.mark.skip  # enable if test__has_file_suffix__real_world passes
                def test__subpath_is_actually_file(self):
                    file = ExPath('/home/gilad/.local/*')
                    for otherfile in path_ctor_permutations('/home/gilad/.local/bin/pip3'):
                        assert file.parent_of(otherfile)
    
    class parent_of:
        def test__sanity(self):
            for path in path_ctor_permutations(giladdirstr):
                assert HOME_EXPATH.parent_of(path)
            for path in path_ctor_permutations('/home'):
                assert not HOME_EXPATH.parent_of(path)
            for path in path_ctor_permutations('/bad'):
                assert not HOME_EXPATH.parent_of(path)
            for path in path_ctor_permutations('/home/bad'):
                assert not HOME_EXPATH.parent_of(path)
            for path in path_ctor_permutations('/home/'):
                assert not HOME_EXPATH.parent_of(path)
            for path in path_ctor_permutations(giladdirstr):
                assert not GILAD_EXPATH.parent_of(path)
            for path in path_ctor_permutations('/home/gilad/'):
                assert not GILAD_EXPATH.parent_of(path)
        
        @pytest.mark.skip
        def test__tilda(self):
            for path in path_ctor_permutations('~/'):
                assert HOME_EXPATH.parent_of(path)
    
    class subpath_of:
        def test__sanity(self):
            assert GILAD_EXPATH.subpath_of(HOME_EXPATH)
            for path in path_ctor_permutations('/home'):
                assert GILAD_EXPATH.subpath_of(path)
            for path in path_ctor_permutations('/home/'):
                assert GILAD_EXPATH.subpath_of(path)
            for path in path_ctor_permutations('/home/gilad'):
                assert not GILAD_EXPATH.subpath_of(path)
            for path in path_ctor_permutations('/home/gilad/'):
                assert not GILAD_EXPATH.subpath_of(path)
        
        @pytest.mark.skip("Fails because not implemented")
        def test__tilda(self):
            for path in path_ctor_permutations('~/'):
                assert GILAD_EXPATH.subpath_of(path)
    
    class suffix:
        class has_file_suffix:
            def test__with_suffix__startswith_path_reg(self):
                # e.g. '.*/py_venv.xml'. should return has suffix (True)
                with_suffix = ExPath('py_venv.xml')
                assert with_suffix.has_file_suffix() is True
                for reg in path_regexes():
                    val = ExPath(f'{reg}{with_suffix}')
                    actual = val.has_file_suffix()
                    assert actual is True
            
            def test__with_suffix__no_stem__startswith_path_reg(self):
                # e.g. '*.xml'. should return has suffix (True)
                with_suffix = ExPath('*.xml')
                actual = with_suffix.has_file_suffix()
                assert actual is True
                for reg in path_regexes():
                    val = ExPath(f'{reg}{with_suffix}')
                    actual = val.has_file_suffix()
                    assert actual is True
            
            def test__with_mixed_regex_suffix(self):
                # e.g. 'py_venv.xm?l'. should return has suffix (True)
                for suffix in mixed_suffixes():
                    with_suffix = ExPath(f'py_venv.{suffix}')
                    actual = with_suffix.has_file_suffix()
                    assert actual is True
            
            def test__everything_mixed_with_regex(self):
                # e.g. '.*/py_v[en]*v.xm?l'. should return has suffix (True)
                assert ExPath('.*/py_v[en]*v.xm?l').has_file_suffix() is True
                mixed_stems = get_permutations_in_size_range(f'{REGEX_CHAR}.py_venv-1257', slice(5), has_letters_and_punc)
                for stem in mixed_stems:
                    for suffix in mixed_suffixes():
                        name = ExPath(f'{stem}.{suffix}')
                        actual = name.has_file_suffix()
                        assert actual is True
                        for reg in path_regexes():
                            val = ExPath(f'{reg}{name}')
                            actual = val.has_file_suffix()
                            assert actual is True
            
            def test__no_suffix__startswith_path_reg(self):
                # e.g. '.*/py_venv'. should return no suffix (False)
                no_suffix = ExPath('py_venv')
                assert no_suffix.has_file_suffix() is False
                for reg in path_regexes():
                    val = ExPath(f'{reg}{no_suffix}')
                    actual = val.has_file_suffix()
                    assert actual is False
            
            def test__no_suffix__endswith_path_reg(self):
                # e.g. 'py_venv.*/'. should return no suffix (False)
                no_suffix = ExPath('py_venv')
                assert no_suffix.has_file_suffix() is False
                for reg in path_regexes():
                    val = ExPath(f'{no_suffix}{reg}')
                    actual = val.has_file_suffix()
                    assert actual is False
            
            def test__no_suffix__surrounded_by_path_reg(self):
                # e.g. '.*/py_venv.*/'. should return no suffix (False)
                no_suffix = ExPath('py_venv')
                assert no_suffix.has_file_suffix() is False
                for reg in path_regexes():
                    for morereg in path_regexes():
                        val = ExPath(f'{morereg}{no_suffix}{reg}')
                        actual = val.has_file_suffix()
                        assert actual is False
            
            def test__real_world(self):
                for nosuffix in ['.*/py_venv.*/',
                                 'file',
                                 'home/gilad/.local/*', ]:
                    assert not ExPath(nosuffix).has_file_suffix()


@pytest.mark.skip
def test____eq__():
    gilad = ExPath(giladdirstr)
    for path in path_ctor_permutations(giladdirstr):
        assert gilad == path
    for path in path_ctor_permutations('~/'):
        assert gilad == path
    gilad = ExPath('~/')
    for path in path_ctor_permutations('~/'):
        assert gilad == path
    for path in path_ctor_permutations(giladdirstr):
        assert gilad == path
