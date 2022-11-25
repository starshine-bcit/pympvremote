from pathlib import Path

URL_FILE = Path(__file__).parent.parent.parent / '.urls'


def save_urls(urls: list[str]) -> None:
    with URL_FILE.open('w', encoding='utf8') as fo:
        for url in urls:
            fo.writelines(f'{url}\n')


def load_urls() -> list[str]:
    data = []
    if URL_FILE.is_file():
        with URL_FILE.open('r', encoding='utf8') as fo:
            data = fo.readlines()
        return [x.strip() for x in data]
    else:
        return []


if __name__ == '__main__':
    pass
