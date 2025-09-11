import pytest
from lotterybr import get_data, InvalidGameError, InvalidTypeError


def test_get_data_invalid_game():
    with pytest.raises(InvalidGameError):
        get_data('invalidgame', 'numbers')

def test_get_data_invalid_type():
    with pytest.raises(InvalidTypeError):
        get_data('megasena', 'invalidtype')

    
if __name__ == '__main__':
    pytest.main()