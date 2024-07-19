import re
import emoji

#remove stopword
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

nltk.download('stopwords')
nltk.download('punkt')
nltk.corpus.stopwords.words('indonesian')


def cleanse_text(text):

    # change word to lower case
    text = text.lower()
    
    # remove emoji
    text = emoji.replace_emoji(text, replace='')
    
    # #remove username @, hashtag# and url https://  \\x \\u
    
    pattern1 = r"(?:@|#|https?://|\\x[0-9A-Fa-f]{2}|\\u[0-9A-Fa-f]{2})\S*"

    #pattern1 = r"(?:\@|\#|https?\://)\S*"
    text = re.sub(pattern1, "", text)

    # remove keyword like user retweet etc.
    pattern2 = r"(user|retweet|xd|url|rt(?:\b|[^a-zA-Z])|cc(?:\b|[^a-zA-Z])|\\r|\\n)\S*"
    text = re.sub(pattern2, "", text)

    # #Removes punctuation marks, mathematical operation characters, etc.
    pattern3 = r"[\=\,\@\*\_\-\!\:\;\?\'\.\"\)\(\{\}\<\>\+\%\$\^\#\/\`\~\|\&\|]"
    text = re.sub(pattern3, "", text)

    # removes \ [ ] (error when add in pattern 3)
    pattern4 = r'[\\\]\[]'
    text = re.sub(pattern4, '', text)

    # remove "wkwkwk"
    pattern7 = r'\bwk\w+'
    text = re.sub(pattern7, '', text)
    
    # remove digit characters
    pattern8 = r'\d+'
    text = re.sub(pattern8, '', text)

    # Removed redundant spaces
    pattern9 = r"(\s+|\\n)"
    text = re.sub(pattern9, ' ', text)

    # #remove repeated char (e.g., yesss)
    pattern10 = r"([A-Za-z])\1{2,}"
    text= re.sub(pattern10, r"\1", text)
    
    # Remove spaces in the first and last sentences
    text = text.rstrip()
    text = text.lstrip()

    return text


# Removing common words that usually have no important meaning (stop words)
stop_words = stopwords.words("indonesian")

def remove_stopwords(text):
    return ' '.join([word for word in word_tokenize(text) if word not in stop_words])