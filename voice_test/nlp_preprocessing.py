import spacy

nlp = spacy.load("en_core_web_sm")


def preprocess_text(text):

    doc = nlp(text)

    tokens = []

    for token in doc:

        if not token.is_space and not token.is_punct:

            lemma = token.lemma_.lower().strip()

            if lemma:
                tokens.append(lemma)

    return tokens