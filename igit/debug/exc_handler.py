import inspect
import sys
import traceback
from types import ModuleType
from typing import List, Union

from igit.util import termcolor

FrameSummaries = List[List[Union[int, traceback.FrameSummary]]]


class ExcHandler:
    def __init__(self, exc: Exception = None, *, capture_locals=True):
        """
        Extracts nicely formatted additional data about the exception. Example:
        ::
            except Exception as e:
                logger.exception('Critical error')  # logs ExcHandler.full() automatically

                # OR

                logger.error('Critical error', exc_info=True)  # logs ExcHandler.summary()

            ...

            try:
                raise PricingHeaderNotFound('no gw pricing config')
            except Exception as e:
                msg = logger.warning(exc_info=True)  # logs ExcHandler.short() and returns its output
                insertRejectDetails(msg)
                """
        # TODO: 1. support for *args then print arg names and values like in 'printdbg'
        #  2. handle 'raise ... from e' better. 'Responsible code: raise ...' isnt interesting (use e.__cause__)
        #  3. if exception raised deliberately ("raise ValueError(...)"), get earlier frame
        self.exc = None  # declare first thing in case anything fails
        try:
            
            if exc:
                tb = sys.exc_info()[2]  # only tb because caller passed exc
                self.exc = exc
            else:
                _, exc, tb = sys.exc_info()  # exc and tb
                self.exc = exc
            self.excArgs = ""
            self.frame_summaries: FrameSummaries = []
            
            if not tb and not exc:
                return
            
            tb_frame_summaries = ExcHandler._extract_tb(tb, capture_locals)
            stack: traceback.StackSummary = traceback.extract_stack()[:-1]  # leave out current frame
            self.frame_summaries = ExcHandler._combine_traceback_and_stack(stack, tb_frame_summaries)
            self.excArgs = ExcHandler.fmt_args(self.exc.args)
        
        except Exception as init_exc:
            self._handle_self_failure(init_exc)
    
    @staticmethod
    def _handle_bad_call_context():
        warning = '\n'.join(["ExcHandler couldn't find any Exception along the trace",
                             "You probably called logger.exception() not inside an exception handling block",
                             "(could also happen when calling logger.error(summarize_exc=True) outside exc handling block"])
        print(warning)
        return ""
    
    def _handle_self_failure(self, init_exc):
        # TODO: this only partially works, needs some work
        tb = sys.exc_info()[2]
        stack: traceback.StackSummary = traceback.extract_stack()[:-2]  # leave out this frame and __init__ frame
        innerframes = inspect.getinnerframes(tb)
        outerframes = inspect.getouterframes(innerframes[0].frame)[1:]  # outerframes are in reverse order
        orig_frame = outerframes[0].frame
        self.frame_summaries = ExcHandler._remove_nonlib_frames(stack)
        self.last.locals = orig_frame.f_locals
        
        if not self.exc:
            try:
                orig_exc = next(val for name, val in self.last.locals.items() if isinstance(val, Exception))  # calculated guess
            except StopIteration:
                orig_exc = None
            self.exc = orig_exc
        args = '\n\t'.join([f'ExcHandler.__init__() ITSELF failed, accidental exception (caught and ok):',
                            f'{init_exc.__class__.__qualname__}: {ExcHandler.fmt_args(init_exc.args)}',
                            f'ORIGINAL exception: {self.excType}: {self.exc}'
                            ])
        self.excArgs = args
    
    @staticmethod
    def _extract_tb(tb, capture_locals: bool) -> FrameSummaries:
        
        extracted_tb = traceback.extract_tb(tb)
        tb_frame_summaries: FrameSummaries = ExcHandler._remove_nonlib_frames(extracted_tb)
        if capture_locals:
            tb_steps_taken = 0
            for i, (f_idx, frame) in enumerate(tb_frame_summaries):
                if f_idx == tb_steps_taken:
                    tb_frame_summaries[i][1].locals = tb.tb_frame.f_locals
                    tb = tb.tb_next
                    tb_steps_taken += 1
                    continue
                
                if f_idx < tb_steps_taken:
                    print(f'REALLY WIERD, f_idx ({f_idx}) < tb_steps_taken ({tb_steps_taken})')
                    continue
                
                if f_idx > tb_steps_taken:
                    steps_to_take = f_idx - tb_steps_taken
                    for _ in range(steps_to_take):
                        tb = tb.tb_next
                        tb_steps_taken += 1
                tb_frame_summaries[i][1].locals = tb.tb_frame.f_locals
                tb = tb.tb_next
                tb_steps_taken += 1
        
        return tb_frame_summaries
    
    @staticmethod
    def _combine_traceback_and_stack(stack: traceback.StackSummary, tb_frame_summaries: FrameSummaries) -> FrameSummaries:
        """The traceback has specific info regarding the exceptions.
        The stack has unspecific info regarding the exceptions, plus info about everything preceding the exceptions.
        This function combines the two."""
        stack_frame_summaries: FrameSummaries = ExcHandler._remove_nonlib_frames(stack)
        overlap_index = ExcHandler._get_frames_overlap_index(stack_frame_summaries, tb_frame_summaries)
        if overlap_index is not None:
            stack_frame_summaries[overlap_index:] = tb_frame_summaries
        else:
            stack_frame_summaries.extend(tb_frame_summaries)
        return stack_frame_summaries
    
    @staticmethod
    def _remove_nonlib_frames(stack: traceback.StackSummary) -> FrameSummaries:
        frame_summaries: FrameSummaries = []
        for i, frame in enumerate(stack):
            irrelevant = 'site-packages' in frame.filename or 'dist-packages' in frame.filename or 'python3' in frame.filename or 'JetBrains' in frame.filename
            if irrelevant:
                continue
            frame_summaries.append([i, frame])
        return frame_summaries
    
    @staticmethod
    def _get_frames_overlap_index(stack_f_summaries: FrameSummaries, tb_f_summaries: FrameSummaries):
        # tb sort: most recent first. stack sort is the opposite → looking to match tb_f_summaries[0]
        for i, fs in enumerate(stack_f_summaries):
            if fs[1].filename == tb_f_summaries[0][1].filename:
                return i
        return None
    
    @staticmethod
    def fmt_args(exc_args) -> str:
        excArgs = []
        for arg in map(str, exc_args):
            if len(arg) > 500:
                arg = f'{arg[:500]}...'
            excArgs.append(arg)
        return ", ".join(excArgs)
    
    @staticmethod
    def _format_locals(lokals: dict) -> str:
        formatted = ""
        for name, val in lokals.items():
            if name.startswith('__') or isinstance(val, ModuleType):
                continue
            if inspect.isfunction(val):
                print(termcolor.lightgrey(f'skipped function: {name}'))
                continue
            typ = type(val)
            val = str(val)
            
            if val.startswith('typing'):
                continue
            if '\n' in val:
                linebreak = '\n\n'  # queries etc
                quote = '"""'
            else:
                linebreak = '\n'
                quote = ''
            formatted += f'\t{name}: {quote}{val}{quote} {termcolor.lightgrey(typ)}{linebreak}'
        return formatted
    
    @property
    def last(self) -> traceback.FrameSummary:
        try:
            return self.frame_summaries[-1][1]
        except Exception as e:
            print('FAILED getting ExcHandler.last()\n', ExcHandler(e).summary())
            fs = traceback.FrameSummary(__name__, -1, 'ExcHandler.last()')
            return fs
    
    @property
    def excType(self):
        return self.exc.__class__.__qualname__
    
    def short(self):
        """Returns 1 line"""
        if not self.exc:
            return ExcHandler._handle_bad_call_context()
        if self.excArgs:
            return f"{self.excType}: {self.excArgs}"
        else:
            return self.excType
    
    def summary(self):
        """Returns 5 lines"""
        if not self.exc:
            return ExcHandler._handle_bad_call_context()
        return '\n'.join([f'{self.excType}, File "{self.last.filename}", line {self.last.lineno} in {self.last.name}()',
                          f'Exception args:',
                          f'\t{self.excArgs}',
                          f'Responsible code:',
                          f'\t{self.last.line}'])
    
    def full(self, limit: int = None):
        """Prints the summary, whole stack and local variables at the scope of exception.
        Limit is 0-based, from recent to deepest (limit=0 means only first frame)"""
        if not self.exc:
            return ExcHandler._handle_bad_call_context()
        description = self.summary()
        honor_limit = limit is not None
        for i, fs in self.frame_summaries:
            if honor_limit and i > limit:
                break
            # from recent to deepest
            description += f'\nFile "{fs.filename}", line {fs.lineno} in {fs.name}()\n\t{fs.line}'
            if fs.locals is not None:
                description += f'\nLocals:\n{ExcHandler._format_locals(fs.locals)}'
        return f'\n{description}\n'


def investigate(loglevel: str = 'INFO', *, logArgs=True, logReturn=True, logExc=True, showLocalsOnExc=True, showLocalsOnReturn=False):
    """
    A decorator that logs common debugging information, like formatted exceptions before they're thrown, argument names and values, return value etc.
    ::
        @logger.investigate(showLocalsOnReturn=True)
        def foo(bar):
            ...
    """
    
    def wrapper(fn):
        
        def decorator(*fnArgs, **fnKwargs):
            term.set_option(print=True)
            fnname = fn.__qualname__
            if '.' in fnname:
                identifier = fnname
            else:
                identifier = f'{inspect.getmodulename(inspect.getmodule(fn).__file__)}.{fnname}'
            
            term.green(f'\nentered {identifier}()')
            
            if logArgs:
                # create a pretty str representation of the function arguments
                args = inspect.getfullargspec(fn)
                arg_names = args.args
                if args.defaults:
                    arg_defaults = dict(zip(arg_names[-len(args.defaults):], args.defaults))
                else:
                    arg_defaults = dict()
                args_str = ", ".join([f'{k}={repr(v)}' for k, v in zip(arg_names, fnArgs)])
                if len(arg_names) < len(fnArgs):
                    args_str += ', ' + f', '.join(map(repr, fnArgs[-len(arg_names):]))
                remaining_arg_names = arg_names[len(fnArgs):]
                fnKwargs_copy = dict(fnKwargs)
                for a in remaining_arg_names:
                    if a in fnKwargs_copy:
                        args_str += f', {a}={repr(fnKwargs_copy[a])}'
                        del fnKwargs_copy[a]
                    elif a in arg_defaults:
                        args_str += f', {a}={repr(arg_defaults[a])}'
                
                if fnKwargs_copy:
                    for k, v in fnKwargs_copy.items():
                        args_str += f', {k}={repr(v)}'
                
                if args_str:
                    term.green(f'args: {fnname}({args_str})')
                else:
                    term.green(f'no args passed')
            
            try:
                retval = fn(*fnArgs, **fnKwargs)
                if logReturn:
                    
                    pretty = pformat(retval, depth=1)
                    if showLocalsOnReturn:
                        # try:
                        #     raise Exception("dummy")
                        # except Exception as e:
                        #     hdlr = ExcHandler(e)
                        # ins_stack = inspect.stack()
                        # tb_stack: traceback.StackSummary = traceback.extract_stack()
                        # tb_stack = ExcHandler._remove_nonlib_frames(tb_stack)
                        pass
                    if len(pretty) > 300:  # don't clutter
                        pretty = f'{pretty[:300]}...'
                    term.green(f'Returning {pretty}')
                
                else:
                    term.green(f'exited {identifier}()')
                
                return retval
            except Exception as e:
                if logExc:
                    e_handler = ExcHandler(e)
                    term.red(e_handler.full())
                
                raise e
            finally:
                term.set_option(print=False)
            #     logger.handlers[0].setFormatter(oldformatter)
        
        return decorator
    
    return wrapper


def printdbg(*args, **kwargs):
    """
    Prints the variable name, its type and value.
    ::
        printdbg(5 + 5, sum([1,2]))
        > 5 + 5 (<class 'int'>):
          10

          sum([1,2]) (<class 'int'>):
          3

    """
    import inspect
    
    def printarg(_name, _val):
        print(f'{_name} ({type(_val)}):', _val, sep='\n', end='\n\n')
    
    if args:
        currframe = inspect.currentframe()
        outer = inspect.getouterframes(currframe)
        frameinfo = outer[1]
        ctx = frameinfo.code_context[0].strip()
        argnames = ctx[ctx.find('(') + 1:-1].split(',')
        if len(argnames) != len(args) + len(kwargs):
            print(f"Too complex statement, try breaking it down to variables")
            return
        for i, val in enumerate(args):
            try:
                name = argnames[i].strip()
            except IndexError:
                continue
            printarg(name, val)
    for name, val in kwargs.items():
        printarg(name, val)
