import base64


def encode_uri(uri: str) -> str:
    """Encodes a string in base64 url safe format.

    Args:
        uri (str): The the string to encode. If using a path object,
            you must pass it as str(path_item)

    Returns:
        str: url safe base64 encoded string
    """    
    return str(base64.urlsafe_b64encode(bytes(uri, encoding='utf-8')), 'utf-8')


def decode_uri(uri: str) -> str:
    """Decodes a string in base64 url safe format.

    Args:
        uri (str): The base64 string to decode

    Returns:
        str: decoded url safe base64 string
    """    
    return str(base64.urlsafe_b64decode(uri), "utf-8")


if __name__ == '__main__':
    pass
