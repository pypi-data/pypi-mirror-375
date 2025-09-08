import os

import unicodedata

from .const import LEMMATIZER_DATA_DIRECTORY_PATH, LEMMATIZER_DICTIONARY_FILENAME_TEMPLATE, LEMMATIZER_NORMALIZATION_TYPE


class Lookup:
    def __init__(self, lang: str):
        self._lang: str = lang

    def get_lemma(self, word: str) -> set[str]:
        word = self._normalize(word)
        return self._get_lemma(word)

    def _normalize(self, text: str) -> str:
        text = unicodedata.normalize(LEMMATIZER_NORMALIZATION_TYPE, text)
        return text

    def _get_lemma(self, word: str) -> set[str]:
        raise NotImplementedError

class DictionaryLookups(Lookup):
    def __init__(self, lang: str):
        super().__init__(lang)
        self._dict = {}
        self._load_from_disk()

    def _get_lemma(self, word: str) -> set[str]:
        lemmas_set = self._dict.get(word.lower(), {word.lower()})
        return lemmas_set

    def _get_file_path(self):
        filename = LEMMATIZER_DICTIONARY_FILENAME_TEMPLATE % self._lang
        path = os.path.join(LEMMATIZER_DATA_DIRECTORY_PATH, filename)
        return path

    def _load_from_disk(self, reset=True):
        path = self._get_file_path()

        if not os.path.isfile(path):
            raise RuntimeError(f"File {path} don’t exists.")

        with open(path) as word_lemma_file:
            try:
                data = {} if reset else self._dict
                for line in word_lemma_file.readlines():
                    line = line.rstrip()

                    if not line:
                        continue

                    line = self._normalize(line)

                    word, lemma = line.split("\t")
                    if word in data:
                        data[word].add(lemma)
                    else:
                        data[word] = {lemma}
                self._dict = data
            except Exception as e:
                raise RuntimeError(f"File {path} is not a valid data.") from e
