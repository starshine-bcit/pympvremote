import base64


def encode_uri(uri: str) -> str:
    return str(base64.urlsafe_b64encode(bytes(uri, encoding='utf-8')), 'utf-8')


def decode_uri(uri: str) -> str:
    return str(base64.urlsafe_b64decode(uri), "utf-8")

if __name__ == '__main__':
    pass