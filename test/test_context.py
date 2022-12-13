from nn_module_selector.context import ModuleContext, get_context

def test_context():
    with ModuleContext('a'):
        assert get_context() == 'a'
        with ModuleContext('b'):
            assert get_context() == 'a.b'
            with ModuleContext('c'):
                assert get_context() == 'a.b.c'
            assert get_context() == 'a.b'
        assert get_context() == 'a'
