import pytest

from dict_traverser import DictTraverser


def test_update():
    obj = {
        'dict': {
            'with': {
                'nested': {
                    'key1': True,
                    'key2': None,
                },
            },
        },
        'in_root': 'value',
    }
    tv = DictTraverser(obj)

    assert tv['dict.with.nested.key1'] is True
    assert tv['dict.with.nested.key2'] is None
    with pytest.raises(KeyError):
        tv['dict.with.nested.key3']
    with pytest.raises(KeyError):
        tv['dict.with.nested.key4']

    tv['dict.with.nested.key3'] = 'new value'
    assert tv['dict.with.nested.key1'] is True
    assert tv['dict.with.nested.key2'] is None
    assert tv['dict.with.nested.key3'] == 'new value'

    tv.set('dict.with.nested.key4', 'another value')
    assert tv['dict.with.nested.key1'] is True
    assert tv['dict.with.nested.key2'] is None
    assert tv['dict.with.nested.key3'] == 'new value'
    assert tv['dict.with.nested.key4'] == 'another value'

    with pytest.raises(KeyError):
        tv['another.nested.array']
    tv['another.nested.array.[3]'] = 3
    assert isinstance(tv['another.nested.array'], list)
    assert len(tv['another.nested.array']) == 4
    assert tv['another.nested.array.[0]'] is None
    assert tv['another.nested.array.[1]'] is None
    assert tv['another.nested.array.[2]'] is None
    assert tv['another.nested.array.[3]'] == 3

    tv['another.nested.array.[0]'] = 0
    tv.set('another.nested.array.[1]', 1)
    assert len(tv['another.nested.array']) == 4
    assert tv['another.nested.array.[0]'] == 0
    assert tv['another.nested.array.[1]'] == 1

    tv['another.nested.array.[2].dict.in.array'] = True
    assert isinstance(tv['another.nested.array.[2].dict'], dict)
    assert tv['another.nested.array.[2].dict.in.array'] is True

    tv['another.nested.array.[4].[2].multidimensional_array'] = True
    assert isinstance(tv['another.nested.array.[4]'], list)
    assert len(tv['another.nested.array']) == 5
    assert len(tv['another.nested.array.[4]']) == 3
    assert tv['another.nested.array.[4].[2].multidimensional_array'] is True

    tv.separator = '+'
    with pytest.raises(KeyError):
        tv['dict+with+nested+key5']
    tv.update({
        'dict': {
            'with': {
                'nested': {
                    'key5': 'another new value',
                },
            },
        },
        'another': {
            'nested': {
                'array_sibling': False,
            },
        },
    })
    assert tv['dict+with+nested+key5'] == 'another new value'
    assert len(tv['dict+with+nested']) == 5
    assert tv['dict+with+nested+key1'] is True
    assert len(tv['another+nested']) == 2
    assert tv['another+nested+array_sibling'] is False
    assert isinstance(tv['another+nested+array'], list)


def test_delete():
    obj = {
        'dict': {
            'with': {
                'nested': {
                    'key1': True,
                    'key2': None,
                },
            },
        },
        'another': {
            'nested': {
                'array': [0, 1, 2, 3, 4],
            },
        },
        'in_root': 'value',
    }
    tv = DictTraverser(obj)

    assert tv['dict.with.nested.key1'] is True
    assert tv['dict.with.nested.key2'] is None
    assert len(tv['another.nested.array']) == 5
    assert tv['in_root'] == 'value'

    del tv['dict.with.nested.key1']
    assert tv['dict.with.nested.key2'] is None
    with pytest.raises(KeyError):
        tv['dict.with.nested.key1']

    del tv['dict.with.nested.key2']
    assert isinstance(tv['dict.with.nested'], dict)
    with pytest.raises(KeyError):
        tv['dict.with.nested.key1']
    with pytest.raises(KeyError):
        tv['dict.with.nested.key2']

    del tv['in_root']
    with pytest.raises(KeyError):
        tv['in_root']

    del tv['dict.with']
    assert len(tv['dict']) == 0

    del tv['another.nested.array.[2]']
    assert len(tv['another.nested.array']) == 4
    assert tv['another.nested.array.[0]'] == 0
    assert tv['another.nested.array.[1]'] == 1
    assert tv['another.nested.array.[2]'] == 3
    with pytest.raises(KeyError):
        del tv['another.nested.array.not_an_index']
    with pytest.raises(IndexError):
        del tv['another.nested.array.[5]']
