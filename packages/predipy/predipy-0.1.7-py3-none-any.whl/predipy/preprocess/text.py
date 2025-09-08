import re

class TextPreprocessor:
    def __init__(self, lowercase=True):
        self.lowercase = lowercase

    def clean(self, text):
        if self.lowercase:
            text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

