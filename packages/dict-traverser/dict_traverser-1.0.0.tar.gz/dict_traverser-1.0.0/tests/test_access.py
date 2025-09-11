import pytest

from dict_traverser import DictTraverser


def test_basic():
    sentinel = object()
    not_found = object()
    obj = {
        'dict': {
            'with': {
                'nested': {
                    'keys': sentinel,
                    'none': None,
                },
            },
        },
        'in_root': True,
    }
    tv = DictTraverser(obj)

    assert tv.obj is obj

    assert tv.get('dict.with.nested.keys') is sentinel
    assert tv['dict.with.nested.keys'] is sentinel
    assert tv.get('dict.with.nested') is obj['dict']['with']['nested']
    assert tv['in_root']

    assert tv['dict.with.nested.none'] is None
    assert tv.get('dict.with.nested.none', not_found) is None

    assert tv.get('dict.with.nested.fail') is None
    assert tv.get('dict.with.nested.fail', not_found) is not_found
    with pytest.raises(KeyError):
        tv['dict.with.nested.fail']


def test_custom_separator():
    sentinel = object()
    not_found = object()
    obj = {
        'dict.with.dots': {
            'and': {
                'nested': {
                    'keys': sentinel,
                    'none': None,
                },
            },
        },
        'nested': {'key': 1},
        'in_root': True,
    }
    tv = DictTraverser(obj, '-')

    assert tv.get('dict.with.dots-and-nested-keys') is sentinel
    assert tv.get('nested.key', not_found) is not_found
    assert tv.get('nested-key', not_found) == 1
    with pytest.raises(KeyError):
        tv['nested.key']

    tv.separator = '.'
    with pytest.raises(KeyError):
        tv['dict.with.dots']


def test_access_nested_array():
    not_found = object()
    obj = {
        'nested': {
            'array': [
                {'key': 1},
                {'key': 2, 'another_array': [None]},
            ],
        },
    }
    tv = DictTraverser(obj)
    assert tv['nested.array.[0].key'] == 1
    assert tv['nested.array.[1].key'] == 2

    assert tv.get('nested.array.[0].another_array.[0]', not_found) is not_found
    assert tv.get('nested.array.[1].another_array.[0]', not_found) is None

    assert tv.get('nested.array[2].key', not_found) is not_found
    with pytest.raises(KeyError):
        tv['nested.array.[2].key']


def test_keys():
    sentinel = object()
    obj = {
        'dict': {
            'with': {
                'nested': {
                    'keys': sentinel,
                    'none': None,
                },
            },
        },
        'in_root': True,
    }
    tv = DictTraverser(obj)
    assert 'dict.with.nested.keys' in tv
    assert 'dict.with.nested.none' in tv
    assert 'dict.with' in tv
    assert 'in_root' in tv
    assert 'dict.with.nested.fail' not in tv
    assert 'fail' not in tv
