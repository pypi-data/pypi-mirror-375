from abc import ABC, abstractmethod


class BaseTranslator(ABC):
    """
    Base class for Translator, define the unified interface for translation
    """
    
    def __init__(self, source: str = 'auto', target: str = 'en'):
        """
        :param source: source language code, default is 'auto'
        :param target: target language code, default is 'en'
        """
        self.source = source
        self.target = target

    @abstractmethod
    def translate(self, text: str) -> str:
        """
        :param text: text to be translated
        :return: translated text
        """
        raise NotImplementedError
