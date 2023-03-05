from common import List, compile


class HttpUrlSupport:
    HTTP_PATTERN = compile('https?://.*')
    IMAGE_PATTERN = compile('(https?://[A-Za-z0-9/.]*?\.(jpg|png|webp))')
    MEDIA_PATTERN = compile('(https?://[A-Za-z0-9/.]*?\.(jpg|png|webp|mp4))')

    @classmethod
    def load(cls,
             filepath: str,
             pattern=HTTP_PATTERN,
             encoding='utf-8'
             ) -> List[str]:
        text: str
        with open(filepath, 'r', encoding=encoding) as f:
            text = f.read()
        return pattern.findall(text)
