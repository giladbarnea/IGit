import re
from typing import Union, Tuple, Any, overload

from more_itertools import partition

from debug.err import DeveloperError
from prompt.options import Options
from prompt.special import Special
from util import termcolor
from util.regex import YES_OR_NO


def _input(s):
    return input(termcolor.white(s)).lower()


AnswerTuple = Tuple[str, Union[str, Special]]


class Prompt:
    answer: Union[AnswerTuple, bool, None]
    
    @staticmethod
    def dialog_string(question: str, options: Options) -> str:
        return f'{question}\n\t{options.str(key="initial")}\t'
    
    @staticmethod
    def get_answer(question: str, options: Options, *, allow_free_input=False) -> Tuple[Any, Any]:
        ans_key = _input(question)
        items = options.items()
        if ans_key not in items:
            if allow_free_input:
                # * Free input
                print(termcolor.green(f"Returning free input: (None, '{ans_key}')"))
                return None, ans_key
            else:
                while ans_key not in items:
                    print(termcolor.yellow(f"Unknown option: '{ans_key}'"))
                    ans_key = _input(question)
        ans_value = items[ans_key]
        answer = ans_key, ans_value
        return answer
    
    def __init__(self, question: str, options: Options, allow_free_input=False):
        self.answer = None
        # don't set(options) because set isn't ordered
        
        # *  Simple Prompt (boolean self.answer)
        if not options:
            # prompt.ask('Coffee?') # TODO: this happens only if passed empty Options()
            self.answer: bool = _input(f'{question} y/n\t').startswith('y')
            return
        
        # *  Complex Prompt
        question = self.dialog_string(question, options)
        answer: AnswerTuple = self.get_answer(question, options, allow_free_input=allow_free_input)
        
        # *  Special Answer
        try:
            special_answer: Special = Special(answer[0])
            
            # answered either of SPECIAL_ANSWERS
            special_answer.execute_answer()
            
            # if special_answer == 'c' → 'answer' var is already 'c' → self.answer = answer
            if special_answer == Special.DEBUG:
                # debugger already started and finished in special_answer.execute_answer() (user 'continue'd here)
                self.answer = self.get_answer(question, options)
            elif special_answer == Special.CONTINUE:
                # special_answer == 'c' → 'answer' var is already 'c' (still relevant?)
                self.answer = Special.CONTINUE.value, Special.CONTINUE
            else:
                raise NotImplementedError
        except ValueError as e:
            # *  DIDN'T answer any special
            if options.all_yes_or_no():
                # prompt.ask('Coffee?', 'yes', 'no', 'quit') → didn't answer 'quit' → boolean self.answer
                self.answer: bool = answer[0] == 'y'
            else:
                # TODO: when does this happen?
                self.answer = answer


class Choice(Prompt):
    answer: AnswerTuple
    
    @staticmethod
    def dialog_string(question: str, options: Options) -> str:
        return f'{question}\n\t{options.str(key="index")}\t'
    
    @staticmethod
    def get_answer(question: str, options: Options, *, allow_free_input=False) -> Tuple[Any, Any]:
        ans_key = _input(question)
        indexeditems = options.indexeditems()
        if ans_key not in indexeditems:
            if allow_free_input:
                # * Free input
                print(termcolor.green(f"Returning free input: (None, '{ans_key}')"))
                return None, ans_key
            else:
                while ans_key not in indexeditems:
                    print(termcolor.yellow(f"Unknown option: '{ans_key}'"))
                    ans_key = _input(question)
        ans_value = indexeditems[ans_key]
        answer = ans_key, ans_value
        return answer
    
    def __init__(self, question: str, options: Options, allow_free_input=False):
        if not options:
            raise TypeError(f'At least one option is required when using Choice (contrary to Prompt)')
        super().__init__(question, options, allow_free_input=allow_free_input)


def generic(prompt: str, *options: str, **kwargs: Union[str, tuple, bool]) -> Prompt:
    """Simplest prompt. `options` are optional, `kwargs` are optional.
    Examples::

        generic('Something bad happened', 'debug', 'quit') → [d], [q]"""
    
    # TODO: consider make Options ctor be able to handle Options('continue')
    special_opts, standard_opts = partition(lambda o: o in Special.full_names(), options)
    options = Options(*standard_opts)
    if 'special_opts' in kwargs:
        if special_opts:
            raise DeveloperError(f"special opts found both in options and kwargs")
        options.set_special_options(kwargs.pop('special_opts'))
    elif special_opts:
        options.set_special_options(special_opts)
    try:
        allow_free_input = kwargs.pop('allow_free_input')
    except KeyError:
        allow_free_input = False
    options.set_kw_options(**kwargs)
    
    return Prompt(prompt, options, allow_free_input=allow_free_input)


@overload
def choose(prompt, *options: str) -> Tuple[str, str]:
    ...


@overload
def choose(prompt, *options: str, **kwargs: Union[str, tuple, bool]) -> AnswerTuple:
    ...


def choose(prompt, *options, **kwargs):
    """Presents `options` by *index*. Expects at least one option."""
    # TODO: test if ok with 'yes'/'no/
    # * options
    options = Options(*options)
    
    # *  special options
    if 'special_opts' in kwargs:
        options.set_special_options(kwargs.pop('special_opts'))
    
    # * allow_free_input
    try:
        allow_free_input = kwargs.pop('allow_free_input')
    except KeyError:
        allow_free_input = False
    
    # *  keyword-actions
    options.set_kw_options(**kwargs)
    return Choice(prompt, options, allow_free_input=allow_free_input).answer


# TODO: implement prompt.ask('yes', 'quit', no='open with current') that returns bool (see search.py _choose_from_many())
def ask(prompt, **kwargs: Union[str, tuple, bool]) -> bool:
    # def ask(prompt, **kwargs: Union[str, tuple, bool]) -> bool:
    """A 'y/n' prompt.

    If `options` contains any "special options", they are presented by key.
    Examples::

        ask('ice cream?', special_opts='quit') → [y], [n], [q]
        ask('pizza?', special_opts=True) → [y], [n], [c], [d], [q]
        ask('burger?', special_opts=('quit', 'debug')) → [y], [n], [q], [d]
        ask('proceed?') → [y], [n]
    :param special_opts:
        If True, special options: ('continue', 'debug', 'quit') are also presented.
        If a str, it has to be one of the special options above.
    """
    options = Options('yes', 'no')
    # *  special options
    if 'special_opts' in kwargs:
        options.set_special_options(kwargs.pop('special_opts'))
    
    # * allow_free_input
    if 'allow_free_input' in kwargs:
        raise ValueError("can't have 'allow_free_input' passed to ask(). always returns a bool.")
    
    # *  keyword-actions
    options.set_kw_options(**kwargs)
    
    return Prompt(prompt, options).answer


@overload
def action(question: str, *actions: str) -> Tuple[str, str]:
    ...


@overload
def action(question: str, *actions: str, **kwargs: Union[str, tuple, bool]) -> AnswerTuple:
    ...


def action(question, *actions, **kwargs):
    """Presents `options` by *key*.
    Compared to `ask()`, `action()` can't be used to prompt for yes/no but instead prompts for strings.
    Example::

        action('uncommitted changes', 'stash & apply', special_opts = True)

    :param actions: must not be empty, and cannot contain 'yes' or 'no'.
    :param special_opts:
        If True, special options: ('continue', 'debug', 'quit') are also presented.
        If a str, it has to be one of the special options above.
        If tuple, has to contain only special options above.
    """
    options = Options(*actions)
    # *  actions
    if not options:
        # similar check in Choice init, because only action Prompt requires at least 1 option
        raise TypeError(f'At least one action is required')
    if options.any_option(lambda o: re.fullmatch(YES_OR_NO, o)):
        raise ValueError(f"Actions cannot include a 'yes' or 'no'. Received: {repr(actions)}")
    
    # *  special options
    if 'special_opts' in kwargs:
        options.set_special_options(kwargs.pop('special_opts'))
    
    # *  keyword-actions
    options.set_kw_options(**kwargs)
    
    print(termcolor.green(f'action() | actions: {repr(actions)}, options: {repr(options)}'))
    return Prompt(question, options).answer
