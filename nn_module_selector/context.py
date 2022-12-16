class ModuleContext:
    """This class provides a hierarchical context.

    """
    _names: list[str] = list()
    def __init__(self, name: str):
        self.__class__._names.append(name)

    def __enter__(self):
        return self

    def __exit__(self, ex_type, ex_value, trace):
        self.__class__._names.pop()

def get_context() -> str:
    return '.'.join(ModuleContext._names)
