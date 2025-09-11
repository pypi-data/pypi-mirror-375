# String Utils

A simple Python package for string utility functions.

## Installation

```bash
pip install string-utils-v1
```

## Usage

```python
from string_utils import reverse, capitalize_words, is_palindrome

result = reverse("hello")
print(result)  # olleh

result = capitalize_words("hello world")
print(result)  # Hello World

result = is_palindrome("racecar")
print(result)  # True
```

## Functions

- `reverse(s)`: Returns the reverse of the string s
- `capitalize_words(s)`: Capitalizes the first letter of each word in s
- `is_palindrome(s)`: Checks if s is a palindrome

## License

MIT License
