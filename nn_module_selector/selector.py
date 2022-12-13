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
        for item in policy:
            if isinstance(item, tuple):
                p = PolicyItem(*item)
            elif isinstance(item, dict):
                p = PolicyItem(**item)
            else:
                p = item
            cls.policy.append(p)
