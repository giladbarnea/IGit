import inspect
import sys
from enum import Enum

from igit.util import termcolor


# from IPython.con

class Special(Enum):
    """Special('c') → Special.CONTINUE"""
    CONTINUE = 'c'
    DEBUG = 'd'
    QUIT = 'q'
    
    @classmethod
    def full_names(cls) -> set:
        """→ {'continue', 'debug', 'quit'}"""
        return set(map(str.lower, Special._member_names_))
    
    @classmethod
    def from_full_name(cls, fullname: str) -> 'Special':
        """'continue' → Special.CONTINUE"""
        try:
            return Special._member_map_[fullname.upper()]
        except KeyError as e:
            raise ValueError(f"'{fullname}' is not a valid {cls.__qualname__}")
    
    def execute_answer(self) -> None:
        print(f'execute_answer() self: ', self)
        if self == Special.QUIT:
            sys.exit('Aborting')
        if self == Special.CONTINUE:
            print(termcolor.italic('continuing'))
            return None
        if self == Special.DEBUG:
            frame = inspect.currentframe()
            up_frames = []
            while frame.f_code.co_filename == __file__:
                frame = frame.f_back
                up_frames.append(frame.f_code.co_name)
            print(termcolor.bold(f'u {len(up_frames)}'), termcolor.grey(repr(up_frames)))
            from ipdb import set_trace
            set_trace(frame, context=30)
            
            return None
        raise NotImplementedError(f"don't support this enum type yet: {self}")
