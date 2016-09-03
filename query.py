from nltk.corpus import conll2000
from nltk.corpus import movie_reviews
from nltk.corpus import reuters
import random
import nltk, re, pprint
from BeautifulSoup import BeautifulSoup
import requests
import sys
from nltk.classify import PositiveNaiveBayesClassifier
from nltk.classify.maxent import MaxentClassifier
from nltk.classify.decisiontree import DecisionTreeClassifier
from nltk.classify.api import MultiClassifierI
import pickle


def remove_tags(raw_text):
    return BeautifulSoup(raw_text).text


def ie_preprocess(sentence):
    #print sentences
    sentence = nltk.word_tokenize(sentence)
    #print sentences
    #sentence = nltk.pos_tag(sentence) 
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


def remove_tags(raw_text):
    return BeautifulSoup(raw_text).text

dataset = [] # 500 samples

for category in brown.categories():
	
	for fileid in brown.fileids(category):
		dataset.append((brown.words(fileids = fileid),category))

dataset = [([w.lower() for w in text],category) for text,category in dataset]

all_words = nltk.FreqDist(w.lower() for w in brown.words())

def feature_extractor(text,bag):
    # bag -> bag of words
    frec = defaultdict(int)
    for word in text:
        if word in bag:
            frec[word] += 1

    return frec

def features(sentence, stopwords):
	words = [w for w in sentence if w not in stopwords]
	# feature = {}
	# for w in words:
	# 	if w in feature:
	# 		feature[w] +=1
	# 	else:
	# 		feature[w] = 1
	return dict(('contains(%s)' % w, True) for w in words)

# training & test 90%-10% naivebayes nltk


def make_req(start=0, rows=200):
    payload = {'q': '*:*', "wt": "json"}
    payload["fq"] = ["DOCUMENT_TYPE:DIRTY_LISTING", "LISTING_POSTED_DATE:[2016-08-01T00:00:00Z TO *]", "LISTING_STATUS:RAW"
    , "UNIT_TYPE:Apartment", "LISTING_CATEGORY:Primary"]

    #payload["fq"].append("LISTING_ID:2206753")

    payload["rows"] = rows
    payload["start"] = start
    payload["fl"] = ["LISTING_DESCRIPTION","LISTING_ID"]
    payload["fl"] += ["LISTING_LATITUDE","LISTING_LONGITUDE"]
    payload["fl"] += ["BEDROOMS", "SIZE"]
    payload["fl"] += ["PROJECT_NAME", "PROJECT_DB_STATUS"]

    host = "http://localhost:8983/solr/collection_mp/select"
    #q=*:*&fq=DOCUMENT_TYPE:DIRTY_LISTING&fq=LISTING_POSTED_DATE:[2016-08-01T00:00:00Z TO *]&fq=LISTING_STATUS:Active&fq=UNIT_TYPE:Apartment&fq=LISTING_CATEGORY:Primary
    #&sort=LISTING_QUALITY_SCORE desc, LISTING_SELLER_COMPANY_SCORE desc&rows=2000&fl=LISTING_DESCRIPTION&wt=json
    req = requests.get(host, params=payload)
    docs = req.json()["response"]["docs"]

    sent = []
    for doc in docs:
    	desc = doc["LISTING_DESCRIPTION"]
    	desc = remove_tags(desc)
    	desc = desc.lower()
    	s = ie_preprocess(desc)
    	sent.append(s)
    	#print s

    return sent

def train_and_test(featureset,n=90):

    random.shuffle(featureset)
    split = int((len(featureset)*n)/100)
    train,test = featureset[:split],featureset[split:]
    classifier = nltk.NaiveBayesClassifier.train(train)
    accuracy= nltk.classify.accuracy(classifier, test)

    return accuracy


def train(positive_featuresets, unlabeled_featuresets, n=90):
	random.shuffle(positive_featuresets)
	random.shuffle(unlabeled_featuresets)

	if (len(positive_featuresets) > len(unlabeled_featuresets)):
		positive_featuresets =  positive_featuresets[:len(unlabeled_featuresets)]
	else:
		unlabeled_featuresets = unlabeled_featuresets[:len(positive_featuresets)]

	split_n = int((len(unlabeled_featuresets)*n)/100)
	train_n, test_n = unlabeled_featuresets[:split_n],unlabeled_featuresets[split_n:]

	print "split_n: ", split_n 

	split_p = int((len(positive_featuresets)*n)/100)
	train_p, test_p = positive_featuresets[:split_p],positive_featuresets[split_p:]

	print "split_p: ", split_p
	train = [(text,1) for text in positive_featuresets]
	train_1 = [(text,0) for text in unlabeled_featuresets]
	train += train_1
	random.shuffle(train)
	
	#classifier = PositiveNaiveBayesClassifier.train(train_p, train_n)
	classifier = DecisionTreeClassifier.train(train)
	#classifier = MultiClassifierI.prob_classify

	rs = {"passed":0,"failed":0}
	for p in test_p:
		if classifier.classify(p):
			rs["passed"] += 1
    	else:
    		rs["failed"] += 1
	#print "test_p", rs
	for n in test_n :
		if not classifier.classify(n):
			rs["passed"] += 1
		else:
			rs["failed"] +=1

	#print rs
	print "Accuracy", rs['passed']*1.0/(rs['passed'] + rs["failed"])*1.0
	# save classifier
	f = open('real_estate_classifier.pickle', 'wb')
	pickle.dump(classifier, f)
	f.close()
	return classifier


# Stopwords as features
stopwords = stopwords.words("english") # 153 words

featureset = [ features(text,stopwords) for text,category in dataset]
featureset_n = [ features(text,stopwords) for text in make_req()] 


classifier = train(featureset, featureset_n, 90)

featureset_nnn = [ features(text,stopwords) for text in make_req(200,200)]

ddd = '''
The other members in the party are sitting Shiromani Akali Dal MLA, Olympian and former hockey captain Pargat Singh and two Ludhiana-based independent MLAs Simarjit Bains and Balwinder Bains. The Bains brothers were Akali supporters before they revolted against the party in the last elections.

The three MLAs met Sidhu at the latter's residence at the Commonwealth Games Village in Delhi on Wednesday where they formalized their ties. Simarjit told TOI they would contest all 117 seats in the state. "We are in touch with a number of MLAs from all parties," he claimed.

"Diler sher ikatthe hue hain... Brave Punjabi men who have opposed the patronage of drugs, mining and transport mafia and poor agriculture policies of the ruling SAD-BJP government have got together," Pargat, who has been suspended from Akali Dal, said. 
'''

ddd = ie_preprocess(ddd.lower())
featureset_nnn.append(features(ddd,stopwords))

t = 0
rst = {}
rst["passed"] = 0
rst["failed"] = 0
for n in featureset_nnn :
	t += 1
	print not classifier.classify(n)
	if not classifier.classify(n):
		rst["passed"] = rst["passed"] + 1
	else:
		rst["failed"] = rst["failed"] + 1
		print n
print "result", rst

print t
print("Accuracy: ",) # around 0.25
