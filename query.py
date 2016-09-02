from nltk.corpus import conll2000
from nltk.corpus import movie_reviews
from nltk.corpus import reuters
import random
import nltk, re, pprint
from BeautifulSoup import BeautifulSoup
import requests
import sys


def remove_tags(raw_text):
    return BeautifulSoup(raw_text).text


def ie_preprocess(sentence):
    #print sentences
    sentence = nltk.word_tokenize(sentence)
    #print sentences
    sentence = nltk.pos_tag(sentence) 
    return sentence



documents = [(list(movie_reviews.words(fileid)), category)
for category in movie_reviews.categories()
              for fileid in movie_reviews.fileids(category)]

random.shuffle(documents)


####################3

from collections import defaultdict
from nltk.corpus import brown,stopwords
import random
import nltk



dataset = [] # 500 samples

for category in brown.categories():
    for fileid in brown.fileids(category):
        dataset.append((brown.words(fileids = fileid),category))

dataset = [([w.lower() for w in text],category) for text,category in dataset]

def feature_extractor(text,bag):
    # bag -> bag of words
    frec = defaultdict(int)
    for word in text:
        if word in bag:
            frec[word] += 1

    return frec

def features(sentence, stopwords):
	words = [w for w in sentence if w not in stopwords]
	return dict(('contains(%s)' % w, True) for w in words)

# training & test 90%-10% naivebayes nltk

def train_and_test(featureset,n=90):

    random.shuffle(featureset)
    split = int((len(featureset)*n)/100)
    train,test = featureset[:split],featureset[split:]
    classifier = nltk.NaiveBayesClassifier.train(train)
    accuracy= nltk.classify.accuracy(classifier, test)
    return accuracy

# Stopwords as features
stopwords = stopwords.words("english") # 153 words

featureset = [(features(text, stopwords),category)for text,category in dataset]

print("Accuracy: ",train_and_test(featureset)) # around 0.25
