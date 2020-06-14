from abc import ABC
from typing import Union, Tuple, Any, overload
import os
from more_termcolor import colors

from igit.prompt.item import Item
from igit.prompt.options import Options, NumOptions, LexicOptions
from igit.prompt.special import Special
from igit.util import misc
from igit.util.misc import try_convert_to_idx
from ipdb import set_trace
import inspect

if os.getenv('IGIT_DEBUG', False):
    def log(*args, **kwargs):
        print(colors.white(f'\n{args}, {kwargs}'))

else:
    def log(*args, **kwargs):
        pass


def _input(s):
    return misc.unquote(input(colors.brightwhite(s)))


AnswerTuple = Tuple[str, Union[str, Special]]


class BasePrompt(ABC):
    answer: Union[AnswerTuple, bool, None]
    options: Options
    
    def __init__(self, question: str, **kwargs):
        self.answer = None
        if 'special_opts' in kwargs:
            self.options.set_special_options(kwargs.pop('special_opts'))
        elif 'flowopts' in kwargs:
            self.options.set_special_options(kwargs.pop('flowopts'))
        try:
            free_input = kwargs.pop('free_input')
        except KeyError:
            free_input = False
        
        # *  keyword-choices
        self.options.set_kw_options(**kwargs)
        
        # *  Complex Prompt
        dialog_string = self.dialog_string(question, free_input=free_input)
        # question = self.dialog_string(question, options, free_input=free_input)
        key, answer = self.get_answer(dialog_string, free_input=free_input)
        
        # *  Special Answer
        try:
            # raises ValueError if answer isn't Special
            special_answer: Special = Special.from_full_name(answer)
            
            special_answer.execute_answer()
            
            if special_answer == Special.DEBUG:
                # debugger already started and finished in special_answer.execute_answer() (user 'continue'd here)
                self.answer = self.get_answer(dialog_string)
            elif special_answer == Special.CONTINUE:
                self.answer = key, Special.CONTINUE
            else:
                raise NotImplementedError
        except ValueError as e:
            # *  DIDN'T answer any special
            if self.options.all_yes_or_no():
                # prompt.confirm('Coffee?', 'yes', 'no', 'quit') → didn't answer 'quit' → boolean self.answer
                self.answer: bool = key.lower() == 'y'
            else:
                self.answer = key, answer
    
    def dialog_string(self, question: str, *, free_input: bool) -> str:
        strings = []
        for optkey, optval in self.options.items.items():
            strings.append(f'[{optkey}]: {optval}')
        options_str = '\n\t'.join(strings)
        question_str = f'{question}'
        if free_input:
            question_str += ' (free input allowed)'
        if options_str:
            return f'{question_str}\n\t{options_str}\t'
        else:
            return question_str + '\t'
    
    @overload
    def get_answer(self, dialog_string: str, *, free_input=False) -> Tuple[str, Union[str, Special, Item]]:
        ...
    
    @overload
    def get_answer(self, dialog_string: str, *, free_input=True) -> Tuple[Union[None, str], Union[str, Special, Item]]:
        ...
    
    def get_answer(self, dialog_string: str, *, free_input=False):
        ans_key = _input(dialog_string)
        items = self.options.items
        if ans_key not in items:
            if ans_key and free_input:
                # * Free input
                print(colors.white(f"Returning free input: (None, '{ans_key}')"))
                return None, ans_key
            else:
                while ans_key not in items:
                    set_trace(inspect.currentframe(), context=30)
                    print(colors.brightyellow(f"Unknown option: '{ans_key}'"))
                    ans_key = _input(dialog_string)
        ans_value = items[ans_key]
        if hasattr(ans_value, 'val'):
            ans_value = ans_value.val
        
        return ans_key, ans_value


class LexicPrompt(BasePrompt):
    options: LexicOptions
    
    def __init__(self, prompt: str, *options: str, **kwargs):
        self.options = LexicOptions(*options)
        super().__init__(prompt, **kwargs)


class Confirmation(LexicPrompt):
    
    def __init__(self, prompt: str, *options: str, **kwargs):
        if 'free_input' in kwargs:
            raise ValueError(f"Confirmation cannot have free input. kwargs: {kwargs}")
        super().__init__(prompt, *options, **kwargs)


class Action(BasePrompt):
    options: LexicOptions
    
    def __init__(self, question: str, *actions: str, **kwargs):
        if not actions:
            raise ValueError(f'At least one action is required')
        self.options = LexicOptions(*actions)
        if self.options.any_item(lambda item: item.is_yes_or_no):
            raise ValueError(f"Actions cannot include a 'yes' or 'no'. Received: {repr(actions)}")
        super().__init__(question, **kwargs)


class Choice(BasePrompt):
    answer: AnswerTuple
    options: NumOptions
    
    def get_answer(self, question: str, *, free_input=False) -> Tuple[Union[None, str, int], Any]:
        ans_key, ans_value = super().get_answer(question, free_input=free_input)
        ans_key = try_convert_to_idx(ans_key)
        return ans_key, ans_value
    
    def __init__(self, question: str, *options: str, **kwargs):
        if not options:
            raise ValueError(f'At least one option is required when using Choice (contrary to Prompt)')
        self.options = NumOptions(*options)
        super().__init__(question, **kwargs)


def generic(prompt: str, *options: str, **kwargs: Union[str, tuple, bool]):
    """Most permissive, a simple wrapper for LexicPrompt. `options` are optional, `kwargs` are optional.
    Examples::

        generic('This and that, continue?', 'yes', flowopts='quit', free_input=True) → [y], [q] (free input allowed)
    """
    
    return LexicPrompt(prompt, *options, **kwargs).answer


@overload
def choose(prompt, *options: str) -> Tuple[str, str]:
    ...


@overload
def choose(prompt, *options: str, **kwargs: Union[str, tuple, bool]) -> AnswerTuple:
    ...


def choose(prompt, *options, **kwargs):
    """Presents `options` by *index*. Expects at least one option"""
    
    answer = Choice(prompt, *options, **kwargs).answer
    return answer


# TODO: implement prompt.confirm('yes', 'quit', no='open with current') that returns bool (see search.py _choose_from_many())
def confirm(prompt, **kwargs: Union[str, tuple, bool]) -> bool:
    """A 'y/n' prompt.

    If `options` contains any "special options", they are presented by key.
    Examples::

        confirm('ice cream?', special_opts='quit') → [y], [n], [q]
        confirm('pizza?', special_opts=True) → [y], [n], [c], [d], [q]
        confirm('burger?', special_opts=('quit', 'debug')) → [y], [n], [q], [d]
        confirm('proceed?') → [y], [n]
    """
    
    return Confirmation(prompt, 'yes', 'no', **kwargs).answer


@overload
def action(question: str, *actions: str) -> Tuple[str, str]:
    ...


@overload
def action(question: str, *actions: str, **kwargs: Union[str, tuple, bool]) -> AnswerTuple:
    ...


def action(question, *actions, **kwargs):
    """Presents `options` by *key*.
    Compared to `confirm()`, `action()` can't be used to prompt for yes/no but instead prompts for strings.
    Example::

        action('uncommitted changes', 'stash & apply', special_opts = True)

    :param actions: must not be empty, and cannot contain 'yes' or 'no'.
    :param special_opts:
        If True, special options: ('continue', 'debug', 'quit') are also presented.
        If a str, it has to be one of the special options above.
        If tuple, has to contain only special options above.
    """
    # options = Options(*actions)
    # # *  actions
    # if not options:
    #     # similar check in Choice init, because only action Prompt requires at least 1 option
    #     raise TypeError(f'At least one action is required')
    # if options.any_item(lambda o: re.fullmatch(YES_OR_NO, o)):
    #     raise ValueError(f"Actions cannot include a 'yes' or 'no'. Received: {repr(actions)}")
    #
    # # *  special options
    # if 'special_opts' in kwargs:
    #     options.set_special_options(kwargs.pop('special_opts'))
    #
    #     # * free_input
    # try:
    #     free_input = kwargs.pop('free_input')
    # except KeyError:
    #     free_input = False
    # # *  keyword-actions
    # options.set_kw_options(**kwargs)
    #
    # print(color.white(f'action() | actions: {repr(actions)}, options: {repr(options)}'))
    # return Prompt(question, options, free_input=free_input).answer
    return Action(question, *actions, **kwargs).answer
