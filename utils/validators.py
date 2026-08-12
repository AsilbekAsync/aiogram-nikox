def validate_age(text: str) -> int | None:
    try:
        age = int(text.strip())
        if 18 <= age <= 99:
            return age
    except ValueError:
        pass
    return None

def validate_height(text: str) -> int | None:
    try:
        height = int(text.strip())
        if 100 <= height <= 250:
            return height
    except ValueError:
        pass
    return None

def validate_weight(text: str) -> int | None:
    try:
        weight = int(text.strip())
        if 30 <= weight <= 200:
            return weight
    except ValueError:
        pass
    return None

def validate_languages(text: str) -> int | None:
    try:
        langs = int(text.strip())
        if 1 <= langs <= 10:
            return langs
    except ValueError:
        pass
    return None

def validate_children(text: str) -> int | None:
    try:
        children = int(text.strip())
        if 0 <= children <= 10:
            return children
    except ValueError:
        pass
    return None

def parse_boolean(text: str) -> bool | None:
    text = text.strip().lower()
    if "ha" in text or "yes" in text:
        return True
    if "yo'q" in text or "yoq" in text or "no" in text:
        return False
    return None
