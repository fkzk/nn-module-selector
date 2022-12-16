from nn_module_selector.context import get_context, ModuleContext
from nn_module_selector.selector import (
    register_module,
    ModuleSelector as ModuleSelectorBase,
)

class InterfaceA:
    def to_str(self): pass
class InterfaceB:
    def to_str(self): pass

class ModuleSelector(ModuleSelectorBase):
    InterfaceA = InterfaceA
    InterfaceB = InterfaceB

class Module:
    def __init__(self):
        self.context = get_context()

@register_module(InterfaceA)
class ModuleA(Module):
    def to_str(self):
        return f'ModuleA: {self.context}'

@register_module(InterfaceA)
class ModuleA2(Module):
    def to_str(self):
        return f'ModuleA2: {self.context}'

@register_module(InterfaceB)
class ModuleB(Module):
    def to_str(self):
        return f'ModuleB: {self.context}'

def test_selector():
    policy = [
        ('InterfaceA', 'ModuleA'),
        ('InterfaceA', 'ModuleA2', lambda c: c.endswith('.b')),
    ]
    ModuleSelector.extend_policy(policy)
    with ModuleContext('a'):
        ms = ModuleSelector()
        module_a = ms.InterfaceA()
        assert module_a.to_str() == 'ModuleA: a'
        with ModuleContext('b'):
            ms = ModuleSelector()
            module_a = ms.InterfaceA()
            assert module_a.to_str() == 'ModuleA2: a.b'
            module_b = ms.InterfaceB()
            assert module_b.to_str() == 'ModuleB: a.b'
        ms = ModuleSelector()
        module_a = ms.InterfaceA()
        assert module_a.to_str() == 'ModuleA: a'
        module_b = ms.InterfaceB()
        assert module_b.to_str() == 'ModuleB: a'
        