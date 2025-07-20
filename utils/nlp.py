from natasha import Segmenter, NewsEmbedding, NewsMorphTagger, Doc, MorphVocab

segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
morph_vocab = MorphVocab()

def extract_keywords_natasha(text: str) -> str:
    doc = Doc(text)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)

    for token in doc.tokens:
        token.lemmatize(morph_vocab)

    lemmas = [
        token.lemma
        for token in doc.tokens
        if token.pos in {'NOUN', 'VERB', 'ADJ'} and token.lemma
    ]

    return " ".join(str(lemma) for lemma in lemmas)
