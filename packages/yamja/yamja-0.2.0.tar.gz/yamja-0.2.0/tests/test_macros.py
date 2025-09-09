from yamja import load_config


def test_macros_upper():
    config = load_config('tests/data/test_macros.yaml')

    # Test the upper macro
    result = config.render('example_upper', name='world')
    expected = 'Hello WORLD'

    assert result == expected


def test_macros_lower():
    config = load_config('tests/data/test_macros.yaml')

    # Test the lower macro
    result = config.render('example_lower', name='WORLD')
    expected = 'Hello world'

    assert result == expected


def test_macros_with_different_cases():
    config = load_config('tests/data/test_macros.yaml')

    # Test upper macro with mixed case
    result_upper = config.render('example_upper', name='HeLLo')
    expected_upper = 'Hello HELLO'
    assert result_upper == expected_upper

    # Test lower macro with mixed case
    result_lower = config.render('example_lower', name='WoRlD')
    expected_lower = 'Hello world'
    assert result_lower == expected_lower
