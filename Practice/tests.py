import main
import generator


code_gen = generator.Generator()


def test_generate_numbers():
    code = int(code_gen.generate_numbers())
    
    if 0 < code < 10**4:
        assert True
    else:
        assert False


def test_generate_chars():
    code = code_gen.generate_chars()
    numbers = '0123456789'
    
    for num in numbers:
        if num in code:
            assert False
    
    assert True
    
