from nltk.corpus import gutenberg, brown
from nltk import FreqDist, word_tokenize, Text
from urllib import request
from bs4 import BeautifulSoup
import requests

def get_gutenberg_stats(fileid):     
    words = gutenberg.words(fileid)
    sents = gutenberg.sents(fileid)
    raw = gutenberg.raw(fileid)
    num_words = len(words)
    
    stats = {
        "words": num_words,
        "sentences": len(sents),
        "characters": len(raw),
        "avg_chars_per_word": round(len(raw) / num_words, 2) if num_words > 0 else 0,
        "ttr": round(len(set(words)) / num_words, 3) if num_words > 0 else 0
    }
    return stats

def get_brown_category_stats(category):
    words = brown.words(categories=category)
    stats = {
        "words": len(words),
        "sentences": len(brown.sents(categories=category)),
        "most_common": FreqDist(words).most_common(5)
    }
    return stats

def text_from_url(url):
    raw_text = request.urlopen(url).read().decode('utf8', errors='ignore')
    tokens = word_tokenize(raw_text)
    return Text(tokens)

def text_from_html(url):
    html_content = requests.get(url).text
    clean_text = BeautifulSoup(html_content, "html.parser").get_text()
    tokens = word_tokenize(clean_text)
    return Text(tokens)
