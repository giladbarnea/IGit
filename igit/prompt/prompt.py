from abc import ABC
from typing import Union, Tuple, Any, overload

from more_termcolor import paint

from igit.prompt.options import Options, IndexedOptions, LexicOptions
from igit.prompt.special import Special
from igit.util import misc
from igit.util.misc import try_convert_to_idx


def _input(s):
    return misc.unquote(input(paint.satwhite(s)))


AnswerTuple = Tuple[str, Union[str, Special]]


class Prompt(ABC):
    answer: Union[AnswerTuple, bool, None]
    options: Options
    
    def __init__(self, question: str, **kwargs):
        self.answer = None
        if 'special_opts' in kwargs:
            self.options.set_special_options(kwargs.pop('special_opts'))
        try:
            allow_free_input = kwargs.pop('allow_free_input')
        except KeyError:
            allow_free_input = False
        
        # *  keyword-choices
        self.options.set_kw_options(**kwargs)
        
        # *  Complex Prompt
        dialog_string = self.dialog_string(question, allow_free_input=allow_free_input)
        # question = self.dialog_string(question, options, allow_free_input=allow_free_input)
        key, answer = self.get_answer(dialog_string, allow_free_input=allow_free_input)
        
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
                # prompt.ask('Coffee?', 'yes', 'no', 'quit') → didn't answer 'quit' → boolean self.answer
                self.answer: bool = key.lower() == 'y'
            else:
                self.answer = key, answer
    
    def dialog_string(self, question: str, *, allow_free_input: bool) -> str:
        strings = []
        for optkey, optval in self.options.items.items():
            strings.append(f'[{optkey}]: {optval}')
        options_str = '\n\t'.join(strings)
        question_str = f'{question}'
        if allow_free_input:
            question_str += ' (free input allowed)'
        if options_str:
            return f'{question_str}\n\t{options_str}\t'
        else:
            return question_str + '\t'
    
    def get_answer(self, dialog_string: str, *, allow_free_input=False) -> Tuple[Union[None, str], Any]:
        ans_key = _input(dialog_string)
        items = self.options.items
        if ans_key not in items:
            if ans_key and allow_free_input:
                # * Free input
                print(paint.white(f"Returning free input: (None, '{ans_key}')"))
                return None, ans_key
            else:
                while ans_key not in items:
                    print(paint.yellow(f"Unknown option: '{ans_key}'"))
                    ans_key = _input(dialog_string)
        ans_value = items[ans_key]
        return ans_key, ans_value


class GenericPrompt(Prompt):
    options: LexicOptions
    
    def __init__(self, prompt: str, *options: str, **kwargs):
        self.options = LexicOptions(*options)
        
        super().__init__(prompt, **kwargs)


class Action(Prompt):
    options: LexicOptions
    
    def __init__(self, question: str, *actions: str, **kwargs):
        if not actions:
            raise TypeError(f'At least one action is required')
        self.options = LexicOptions(*actions)
        if self.options.any_item(lambda item: item.is_yes_or_no):
            raise ValueError(f"Actions cannot include a 'yes' or 'no'. Received: {repr(actions)}")
        super().__init__(question, **kwargs)


class Choice(Prompt):
    answer: AnswerTuple
    options: IndexedOptions
    
    def get_answer(self, question: str, *, allow_free_input=False) -> Tuple[Union[None, str, int], Any]:
        ans_key, ans_value = super().get_answer(question, allow_free_input=allow_free_input)
        ans_key = try_convert_to_idx(ans_key)
        return ans_key, ans_value
    
    def __init__(self, question: str, *options: str, **kwargs):
        if not options:
            raise TypeError(f'At least one option is required when using Choice (contrary to Prompt)')
        self.options = IndexedOptions(*options)
        
        super().__init__(question, **kwargs)


def generic(prompt: str, *options: str, **kwargs: Union[str, tuple, bool]):
    """Most permissive, a simple wrapper for Prompt ctor. `options` are optional, `kwargs` are optional.
    The only function that returns a Prompt object.
    Examples::

        generic('This and that, continue?', 'yes', 'quit') → [y], [q]
    """
    
    return GenericPrompt(prompt, *options, **kwargs).answer


@overload
def choose(prompt, *options: str) -> Tuple[str, str]:
    ...


@overload
def choose(prompt, *options: str, **kwargs: Union[str, tuple, bool]) -> AnswerTuple:
    ...


def choose(prompt, *options, **kwargs):
    """Presents `options` by *index*. Expects at least one option"""
    # TODO: test if ok with 'yes'/'no/
    
    return Choice(prompt, *options, **kwargs).answer


# TODO: implement prompt.ask('yes', 'quit', no='open with current') that returns bool (see search.py _choose_from_many())
def ask(prompt, **kwargs: Union[str, tuple, bool]) -> bool:
    """A 'y/n' prompt.

    If `options` contains any "special options", they are presented by key.
    Examples::

        ask('ice cream?', special_opts='quit') → [y], [n], [q]
        ask('pizza?', special_opts=True) → [y], [n], [c], [d], [q]
        ask('burger?', special_opts=('quit', 'debug')) → [y], [n], [q], [d]
        ask('proceed?') → [y], [n]
    """
    
    return GenericPrompt(prompt, 'yes', 'no', **kwargs).answer


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
    #     # * allow_free_input
    # try:
    #     allow_free_input = kwargs.pop('allow_free_input')
    # except KeyError:
    #     allow_free_input = False
    # # *  keyword-actions
    # options.set_kw_options(**kwargs)
    #
    # print(paint.white(f'action() | actions: {repr(actions)}, options: {repr(options)}'))
    # return Prompt(question, options, allow_free_input=allow_free_input).answer
    return Action(question, *actions, **kwargs).answer
