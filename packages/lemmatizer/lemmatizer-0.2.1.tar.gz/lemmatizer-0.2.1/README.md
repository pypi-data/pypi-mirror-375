# Lemmatizer

A simple approach to get lemma of words.
Those lemmas are loaded from a dictionary.

## Supported languages

| language | code |
| -------- | ---- |
| french | fr |

## Usage

```python
from lemmatizer import Lemmatizer

nlp = Lemmatizer()
for lemma in nlp.get_lemma("moulons", "fr"):
    print(lemma)
```
