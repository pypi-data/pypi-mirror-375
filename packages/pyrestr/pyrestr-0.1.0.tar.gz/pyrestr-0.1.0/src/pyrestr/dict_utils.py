def keybyval(dictionary: dict, value):
    """Returns the first key in the dictionary that matches the given value."""
    for key, val in dictionary.items():
        if val == value:
            return key
    return None
