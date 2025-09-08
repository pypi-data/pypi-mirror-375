from googletranslatepy import Translator

from .base import BaseTranslator


class GoogleTranslator(BaseTranslator):
    """Google Translator with `googletranslatepy`
    """
    
    def __init__(self, source: str = 'auto', target: str = 'en'):
        super().__init__(source, target)
        self.translator = Translator(source=source, target=target)

    def translate(self, text: str) -> str:
        """
        :param text: text to be translated
        :return: translated text
        """
        return self.translator.translate(text)
