from yamja import load_config


def test_include_yaml():
    result = load_config('tests/data/include_test.yaml')

    expected = {
        'top': {
            'first_key': {'name': 'first_name_value'},
            'second_key': {'name': 'second_name_value'},
            'third_key': {'name': 'this will override the value from include_second.yaml'},
            'other_key': {'name': 'other_name_value'}
        }
    }

    assert result.data == expected
