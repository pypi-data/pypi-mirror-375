from collections import Counter

def find_duplicates(data):
    """
    Returns a list of duplicate elements from the given iterable.
    Works for lists, tuples, strings, etc.
    """
    seen = set()
    duplicates = set()

    for item in data:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)

    return list(duplicates)


def count_duplicates(data):
    """
    Returns a dictionary of duplicate elements with their frequencies.
    Works for lists, tuples, strings, etc.
    """
    freq = Counter(data)
    duplicates = {item: count for item, count in freq.items() if count > 1}
    return duplicates
