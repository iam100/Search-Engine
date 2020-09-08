import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from Stemmer import Stemmer
import re

nltk.download('stopwords')
nltk.download('punkt')

stop_words = set(stopwords.words('english'))
stemmer = Stemmer('english')


def cleanupText(stats):
    global stop_words
    global stemmer
    
    stats = stats.encode("ascii", errors="ignore").decode()
    stats = re.sub(r'http[^\ ]*\ ',r' ',stats)
    stats = re.sub(r'&nbsp;|&lt;|&gt;|&amp;|&quot;|&apos;', r' ',stats)
    stats = re.sub(r'\`|\~|\!|\@|\#|\"|\'|\$|\%|\^|\&|\*|\(|\)|\-|\_|\=|\+|\\|\||\]|\[|\}|\{|\;|\:|\/|\?|\.|\>|\,|\<|\'|\n|\||\|\/"',r' ',stats)
    stats = stats.split()
    stats = [i for i in stats if not i in stop_words]
    stats = stemmer.stemWords(stats)
    return stats