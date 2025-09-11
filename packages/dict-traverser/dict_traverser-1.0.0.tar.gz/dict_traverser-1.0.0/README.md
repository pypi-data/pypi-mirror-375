# dict-traverser

Simple wrapper to work with deeply nested Python dictionaries and lists using dot-notation paths.

It supports safe lookups, nested updates, automatic structure creation, array indexing, and key deletion—ideal for working with JSON-like data structures.

## Installation

```bash
pip install dict-traverser
```

## Usage

### `DictTraverser`

```python
from dict_traverser import DictTraverser

data = {
    'user': {
        'profile': {
            'name': 'Alice',
            'emails': ['first@example.com', 'second@example.com'],
        },
    },
}

tv = DictTraverser(data)

# Get values
print(tv['user.profile.name'])  # 'Alice'
print(tv.get('user.profile.age', 30))  # 30 (default)
print(tv['user.profile.emails.[0]']) # first@example.com

# Set values (automatically creates the necessary structures)
tv['user.profile.age'] = 25
tv['user.profile.emails.[2]'] = 'third@example.com'

# Delete values
del tv['user.profile.name']

# Update with another dict
tv.update({
    'user': {'profile': {'country': 'US'}},
})

# Access the underlying dictionary
print(tv.obj)

# Resulting dictionary after the updates above
{
    'user': {
        'profile': {
            # Name got deleted
            'emails': [
                'first@example.com',
                'second@example.com',
                'third@example.com', # Added to the array
            ],
            'age': 25, # Added by setting the key
            'country': 'US', # Added by update() call
        },
    },
}
```

### `DictTraverser` with custom separator

If the keys in your data include dots (`.`), you can provide a custom separator to `DictTraverser`:

```python
from dict_traverser import DictTraverser

data = {
    'user': {
        'settings': {
            'theme': 'dark',
            'device.type': 'mobile',
        },
    },
}
tv = DictTraverser(data, '.')  # '.' is the default

try:
    tv['user.settings.device.type']
except KeyError:
    # Will raise KeyError because it tried to access a
    # dictionary called `api` inside `settings`
    pass

tv = DictTraverser(data, '+')  # Now use + signs for separators
print(tv['user+settings+theme'])  # dark

tv.separator = '|'  # You can also change the separator after creation
print(tv['user|settings|device.type'])  # mobile
```

### `unwind`

Utility function to convert a nested dictionary to a one-level-deep dictionary with dot-notation keys

```python
from dict_traverser import unwind

data = {
    'user': {
        'profile': {
            'name': 'Alice',
            'emails': ['first@example.com', 'second@example.com'],
        },
    },
}
print(unwind(data))
{
    'user.profile.name': 'Alice',
    'user.profile.emails': ['first@example.com', 'second@example.com'],
}

print(unwind(data, separator='|'))
{
    'user|profile|name': 'Alice',
    'user|profile|emails': ['first@example.com', 'second@example.com'],
}

print(unwind(data, initial_key='prefix'))
{
    'prefix.user.profile.name': 'Alice',
    'prefix.user.profile.emails': ['first@example.com', 'second@example.com'],
}
```
