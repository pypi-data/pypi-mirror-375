from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import pandas as pd

def bow_vectorize(corpus):    # Bag of Words
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    df = pd.DataFrame(X.toarray(), columns=feature_names)
    return df, feature_names

def tfidf_vectorize(corpus):    # TF-IDF
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    df = pd.DataFrame(X.toarray(), columns=feature_names)
    return df, feature_names
