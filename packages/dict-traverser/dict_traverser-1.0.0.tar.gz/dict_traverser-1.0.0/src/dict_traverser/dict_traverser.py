import re

_INDEX_REGEX = r'\[(\d+)\]'


def unwind(obj: dict, initial_key: str | None = None, separator='.'):
    def convert(obj: dict, initial_key: str | None = None):
        for key, value in obj.items():
            if initial_key:
                new_key = f'{initial_key}{separator}{key}'
            else:
                new_key = key
            if isinstance(value, dict):
                convert(value, new_key)
            else:
                new_obj[new_key] = value

    if not isinstance(obj, dict):
        return {}

    new_obj = {}
    convert(obj, initial_key)
    return new_obj


def _insert_value(value, index, arr: list):
    if index < 0:
        raise IndexError('Index cannot be negative')

    if index >= len(arr):
        arr.extend([None] * (index - len(arr) + 1))

    arr[index] = value


class DictTraverser:
    def __init__(self, obj: dict, separator='.'):
        self.obj = obj
        self.separator = separator

    def get(self, key: str, default=None):
        sub_obj = self.obj
        sub_key = key
        for sub_key in key.split(self.separator):
            array_index_match = re.match(_INDEX_REGEX, sub_key)
            if array_index_match is not None:
                if not isinstance(sub_obj, list):
                    return default
                index = int(array_index_match.group(1))
                if len(sub_obj) <= index:
                    return default
                sub_obj = sub_obj[index]
            elif sub_key not in sub_obj:
                return default
            else:
                sub_obj = sub_obj[sub_key]

        return sub_obj

    def update(self, obj: dict):
        unwound_obj = unwind(obj, separator=self.separator)
        for key, value in unwound_obj.items():
            self.set(key, value)

    def set(self, key: str, value):
        sub_obj = self.obj
        iter_keys = []
        all_keys = key.split(self.separator)
        for sub_index, sub_key in enumerate(all_keys[:-1]):
            match = re.match(_INDEX_REGEX, sub_key)
            iter_keys.append(sub_key)
            current = self.get(self.separator.join(iter_keys))
            if isinstance(current, (dict, list)):
                sub_obj = current
            elif current is None:
                next_match = re.match(_INDEX_REGEX, all_keys[sub_index + 1])
                if next_match is not None:
                    new_obj = []
                else:
                    new_obj = {}

                if match is not None:
                    index = int(match.group(1))
                    _insert_value(new_obj, index, sub_obj)
                    sub_obj = new_obj
                else:
                    sub_obj[sub_key] = new_obj
                    sub_obj = sub_obj[sub_key]
            elif not isinstance(current, dict):
                raise KeyError(f'Element at `{".".join(iter_keys)}` is not a dictionary')

        last_key = all_keys[-1]
        match = re.match(_INDEX_REGEX, last_key)

        last_obj = self.get(self.separator.join(iter_keys))
        if match is not None:
            index = int(match.group(1))
            _insert_value(value, index, last_obj)
        else:
            if last_obj is None:
                last_obj = self.obj
            last_obj[last_key] = value

    def __setitem__(self, key, value):
        self.set(key, value)

    def __getitem__(self, key: str):
        sentinel = object()
        value = self.get(key, default=sentinel)
        if value is sentinel:
            raise KeyError(key)
        return value

    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.obj)})'

    def __bool__(self):
        return bool(self.obj)

    def __contains__(self, key: str):
        sentinel = object()
        return self.get(key, sentinel) is not sentinel

    def __delitem__(self, key: str):
        keys = key.split(self.separator)
        keys, final_key = self.separator.join(keys[:-1]), keys[-1]
        if keys:
            parent = self[keys]
        else:
            parent = self.obj

        if isinstance(parent, list):
            array_index_match = re.match(_INDEX_REGEX, final_key)
            if array_index_match is None:
                raise KeyError(f'"{keys}" is an array, but "{final_key}" is not an index')
            index = int(array_index_match.group(1))
            parent.pop(index)
        else:
            del parent[final_key]
