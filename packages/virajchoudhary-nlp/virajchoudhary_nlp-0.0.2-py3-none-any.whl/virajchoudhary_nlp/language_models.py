from nltk.util import ngrams
from collections import Counter

def generate_ngrams(tokens, n):      # N-grams
    n_grams = ngrams(tokens, n)
    return [" ".join(gram) for gram in n_grams]
 
def get_ngram_counts(corpus_tokens, n):      # N-gram Counts
    n_grams = ngrams(corpus_tokens, n) 
    return Counter(n_grams)
