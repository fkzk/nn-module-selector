from dataclasses import dataclass, field
from functools import partial
from typing import Any, Callable, Optional, Sequence, TypeVar, Union

from nn_module_selector.context import get_context

Interface = TypeVar('Interface')
Module = TypeVar('Module')

_INTERFACE2MODULES: dict[type[Interface], dict[str, type[Module]]] = dict()

def register_module(
    interface: type[Interface],
    *optional_interfaces: Sequence[type[Interface]],
    alias: Optional[Union[str, Sequence[str]]] = None,
) -> Callable[[type[Module]], type[Module]]:
    """Generates module registerer for the specified module interfaces.

    Args:
        interface (type[Interface]):
            An interface of which the Module subclass is an implementation.
        alias (Optional[Union[str, Sequence[str]]], optional):
            Aliases of the Module subclass. Defaults to None.

    Returns:
        Callable[[type[Module]], type[Module]]:
            A decorator of the Module subclass that register the subclass as an 
            implementation of the specified module interfaces.
    """
    interface = [interface, ] + list(optional_interfaces)
    def _register_module(module_cls):
        name = [module_cls.__name__, module_cls.__qualname__]
        if isinstance(alias, str):
            name.append(alias)
        elif alias is not None:
            name.extend(alias)
        for _interface in interface:
            if _interface not in _INTERFACE2MODULES:
                _INTERFACE2MODULES[_interface] = dict()
            for n in name:
                _INTERFACE2MODULES[_interface][n] = module_cls
        return module_cls
    return _register_module

@dataclass
class PolicyItem:
    """A dataclass representing a policy entry for selecting the module to apply.

    - interface_name (str): The name of the target Interface class.
    - module_name (str): The name of the Module subclass to apply.
    - condition_fn (Callable[[str], bool]):
        A function that returns whether to apply this policy from the context name.
        By default, this is set by what always returns `True` .
    - module_kwargs (dict[str, Any]):
        The keyword arguments for initializing the Module subclass.
        The specified arguments should not be duplicated with the interface 
        initialization arguments.
    """
    interface_name: str
    module_name: str
    condition_fn: Callable[[str], bool] = lambda _: True
    module_kwargs: dict[str, Any] = field(default_factory=dict)

class ModuleSelector:
    policy: list[PolicyItem] = list()
    def __init__(self):
        self.context = get_context()
        for interface, candidates in _INTERFACE2MODULES.items():
            i_name = interface.__name__
            module_cls = self._select_module_cls(i_name, candidates)
            setattr(self, i_name, module_cls)

    def _select_module_cls(
        self,
        interface_name: str,
        candidates: dict[str, type[Module]],
    ):
        if len(candidates) == 1:
            return list(candidates.values())[0]
        module_cls = candidates.get(interface_name)
        for policy_item in self.policy:
            if all([
                policy_item.interface_name == interface_name,
                policy_item.condition_fn(self.context),
            ]):
                module_name = policy_item.module_name
                module_cls = candidates[module_name]
        module_cls = partial(module_cls, **policy_item.module_kwargs)
        return module_cls

    @classmethod
    def extend_policy(
        cls,
        policy: Sequence[Union[PolicyItem, tuple, dict]]
    ):
        """Register new policies for choosing modules.

        Args:
            policy (Sequence[Union[PolicyItem, tuple, dict]]):
                A sequence of policies to choose modules.
                Every policy entry represents its target interface,
                the concrete Module subclass to apply, the condition to apply,
                and the options for initializing the module.
        """
        for item in policy:
            if isinstance(item, tuple):
                p = PolicyItem(*item)
            elif isinstance(item, dict):
                p = PolicyItem(**item)
            else:
                p = item
            cls.policy.append(p)
