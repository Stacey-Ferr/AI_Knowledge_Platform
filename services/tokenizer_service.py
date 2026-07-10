import spacy

class Tokenizer:
    def __init__(self):
        """
            Loads the spacy model
        """
        self.nlp = spacy.load("en_core_web_sm")
    
    def tokenize(self, text:str) -> list[str]:
        """
            lemma_ returns the base or dictionary form of a word, e.g. run from running
            Tokenization is done for each word if it is not a stop word, punctuation or a space.
        """
        doc = self.nlp(text)
        return [ 
                    token.lemma_.lower() for token in doc
                                            if not token.is_stop
                                            and not token.is_punct
                                            and not token.is_space
                ]