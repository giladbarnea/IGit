import os
from abc import ABC
from typing import Union, Tuple, Any, overload

from igit_debug.investigate import logonreturn, logreturn
from more_termcolor import colors

from igit.abcs import prettyrepr
from igit.prompt.item import MutableItem, FlowItem, LexicItem
from igit.prompt.options import Options, NumOptions, LexicOptions
from igit.util import misc
from igit.util.misc import try_convert_to_idx, darkprint


def _input(s):
    return misc.unquote(input(colors.brightwhite(s)))


# (str, str) or (str, FlowItem)
AnswerTuple = Union[Tuple[str, MutableItem], Tuple[str, FlowItem], Tuple[str, LexicItem]]
Answer = Union[AnswerTuple, bool]


@prettyrepr
class BasePrompt:
    # bool or (str, MutableItem)
    answer: Answer
    options: Options
    
    @logonreturn('self.answer', types=True)
    def __init__(self, question: str, **kwargs):
        # noinspection PyTypeChecker
        self.answer: Answer = None
        if 'flowopts' in kwargs:
            self.options.set_flow_opts(kwargs.pop('flowopts'))
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
        darkprint(f'{repr(self)} key, answer: {key}, {answer}')
        # *  FlowItem Answer
        try:
            # raises ValueError if answer isn't FlowItem
            # special_answer: FlowItem = FlowItem.from_full_name(answer)
            flow_answer: FlowItem = FlowItem(answer)
            darkprint(f'{repr(self)} flow_answer: {flow_answer}')
            flow_answer.execute()
            
            if flow_answer.DEBUG:
                # debugger already started and finished in flow_answer.execute() (user 'continue'd here)
                self.answer = self.get_answer(dialog_string)
            elif flow_answer.CONTINUE:
                self.answer: Tuple[str, FlowItem] = key, flow_answer
            else:
                raise NotImplementedError
        except ValueError as e:
            # *  DIDN'T answer any flow
            
            if hasattr(answer, "is_yes_or_no") and answer.is_yes_or_no:
                # prompt.confirm('Coffee?', 'yes', 'no', 'quit') → didn't answer 'quit' → boolean self.answer
                darkprint(f'{repr(self)} no flow chosen, answer is yes / no. key: {repr(key)}, answer: {repr(answer)}, options: {self.options}')
                self.answer: bool = key.lower() in ('y', 'yes')
            else:
                darkprint(f'{repr(self)} no flow chosen, answer is not yes / no. key: {repr(key)}, answer: {repr(answer)}, options: {self.options}')
                self.answer: Tuple[str, MutableItem] = key, answer
    
    def __repr__(self) -> str:
        return f'{self.prepr()}(answer={repr(self.answer)}, options={repr(self.options)})'
    
    def dialog_string(self, question: str, *, free_input: bool) -> str:
        strings = []
        for optkey, optval in self.options.items.items():
            strings.append(f'[{optkey}]: {optval}')
        options_str = '\n\t'.join(strings)
        question_str = f'{question}'
        # if free_input:
        #     question_str += ' (free input allowed)'
        if options_str:
            dialog_string = f'{question_str}\n\t{options_str}\n\t'
        else:
            dialog_string = question_str + '\n\t'
        if free_input:
            dialog_string += '(free input allowed)\n\t'
        return dialog_string
    
    @overload
    def get_answer(self, dialog_string: str, *, free_input=False) -> AnswerTuple:
        ...
    
    @overload
    def get_answer(self, dialog_string: str, *, free_input=True) -> Tuple[None, str]:
        ...
    
    @logreturn
    def get_answer(self, dialog_string: str, *, free_input=False):
        ans_key = _input(dialog_string)
        items = self.options.items
        if ans_key not in items:
            if ans_key and free_input:
                # * Free input
                print(colors.white(f"Returning free input: (None, '{ans_key}')"))
                return None, ans_key
            else:
                # TODO: this doesnt account for free_input = True, but no ans_key ('')
                while ans_key not in items:
                    print(colors.brightyellow(f"Unknown option: '{ans_key}'"))
                    ans_key = _input(dialog_string)
        ans_value = items[ans_key]
        # this is commented out because BasePrompt init needs to check if answer.is_yes_or_no
        # if hasattr(ans_value, 'value'):
        #     ans_value = ans_value.value
        
        return ans_key, ans_value


class LexicPrompt(BasePrompt):
    options: LexicOptions
    answer: Tuple[str, LexicItem]
    
    def __init__(self, prompt: str, *options: str, **kwargs):
        self.options = LexicOptions(*options)
        super().__init__(prompt, **kwargs)


class Confirmation(LexicPrompt):
    options: LexicOptions
    answer: bool
    
    def __init__(self, prompt: str, *options: str, **kwargs):
        if 'free_input' in kwargs:
            raise ValueError(f"Confirmation cannot have free input. kwargs: {kwargs}")
        super().__init__(prompt, *options, **kwargs)


class Action(BasePrompt):
    options: LexicOptions
    answer: Tuple[str, LexicItem]
    
    def __init__(self, question: str, *actions: str, **kwargs):
        if not actions:
            raise ValueError(f'At least one action is required')
        self.options = LexicOptions(*actions)
        if self.options.any_item(lambda item: item.is_yes_or_no):
            raise ValueError(f"Actions cannot include a 'yes' or 'no'. Received: {repr(actions)}")
        super().__init__(question, **kwargs)


class Choice(BasePrompt):
    options: NumOptions
    answer: Tuple[str, MutableItem]
    
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


def choose(prompt, *options: str, **kwargs: Union[str, tuple, bool]) -> Tuple[str, MutableItem]:
    """Presents `options` by *index*. Expects at least one option"""
    
    answer = Choice(prompt, *options, **kwargs).answer
    return answer


# TODO: implement prompt.confirm('yes', 'quit', no='open with current') that returns bool (see search.py _choose_from_many())
def confirm(prompt, **kwargs: Union[str, tuple, bool]) -> bool:
    """A 'y/n' prompt.

    If `options` contains any "special options", they are presented by key.
    Examples::

        confirm('ice cream?', flowopts='quit') → [y], [n], [q]
        confirm('pizza?', flowopts=True) → [y], [n], [c], [d], [q]
        confirm('burger?', flowopts=('quit', 'debug')) → [y], [n], [q], [d]
        confirm('proceed?') → [y], [n]
    """
    
    return Confirmation(prompt, 'yes', 'no', **kwargs).answer


def action(question, *actions, **kwargs: Union[str, tuple, bool]) -> Tuple[str, LexicItem]:
    """Presents `options` by *key*.
    Compared to `confirm()`, `action()` can't be used to prompt for yes/no but instead prompts for strings.
    Example::

        action('uncommitted changes', 'stash & apply', flowopts = True)

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
    # if 'flowopts' in kwargs:
    #     options.set_flow_opts(kwargs.pop('flowopts'))
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
