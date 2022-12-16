class ModuleContext:
    """This class provides a global hierarchical context.

    Example:
        >>> with ModuleContext('a'):
        ...     ctx1 = get_context() # ctx1 = 'a'
        ...     with ModuleContext('b'):
        ...         ctx2 = get_context('b') # ctx2 = 'a.b'
        ...     ctx3 = get_context() # ctx3 = 'a'
    """
    _names: list[str] = list()
    def __init__(self, name: str):
        self.__class__._names.append(name)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, trace):
        self.__class__._names.pop()

def get_context() -> str:
    """Returns the current context name.

    Returns:
        str: The current context name. The hierarchy sign is ".".
    """
    return '.'.join(ModuleContext._names)
