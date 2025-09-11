def reverse(s):
    """Return the reverse of the string s."""
    return s[::-1]

def capitalize_words(s):
    """Capitalize the first letter of each word in s."""
    return s.title()

def is_palindrome(s):
    """Check if s is a palindrome."""
    cleaned = ''.join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]
