import string
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import pos_tag

def to_lowercase(text):    #lowercase
    return text.lower()

def remove_punctuation(text):    #punctuation
    return text.translate(str.maketrans('', '', string.punctuation))

def tokenize_words(text): #tokenization
    return word_tokenize(text)

def remove_stopwords(tokens):     #stopwords
    stop_words = set(stopwords.words('english'))
    return [token for token in tokens if token.lower() not in stop_words]

def stem_words(tokens):     #stemming
    stemmer = PorterStemmer()
    return [stemmer.stem(token) for token in tokens]
 
def lemmatize_words(tokens):    #lemmatization
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(token) for token in tokens]

def get_pos_tags(tokens):    #POS tagging
    return pos_tag(tokens)

