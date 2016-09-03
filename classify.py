from collections import defaultdict
from nltk.corpus import brown,stopwords
import random
import nltk
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


ddd = '''
The other members in the party are sitting Shiromani Akali Dal MLA, Olympian and former hockey captain Pargat Singh and two Ludhiana-based independent MLAs Simarjit Bains and Balwinder Bains. The Bains brothers were Akali supporters before they revolted against the party in the last elections.

The three MLAs met Sidhu at the latter's residence at the Commonwealth Games Village in Delhi on Wednesday where they formalized their ties. Simarjit told TOI they would contest all 117 seats in the state. "We are in touch with a number of MLAs from all parties," he claimed.

"Diler sher ikatthe hue hain... Brave Punjabi men who have opposed the patronage of drugs, mining and transport mafia and poor agriculture policies of the ruling SAD-BJP government have got together," Pargat, who has been suspended from Akali Dal, said. 
'''

# Stopwords as features
stopwords = stopwords.words("english") # 153 words

def features(sentence, stopwords):
	words = [w for w in sentence if w not in stopwords]
	# feature = {}
	# for w in words:
	# 	if w in feature:
	# 		feature[w] +=1
	# 	else:
	# 		feature[w] = 1
	return dict(('contains(%s)' % w, True) for w in words)

def remove_tags(raw_text):
    return BeautifulSoup(raw_text).text




def ie_preprocess(sentence):
    #print sentences
    sentence = nltk.word_tokenize(sentence)
    #print sentences
    #sentence = nltk.pos_tag(sentence) 
    return sentence


def main(ddd, listing_ids):
	f = open('real_estate_classifier.pickle', 'rb')
	classifier = pickle.load(f)
	f.close()
	#print "ssdj", listing_ids
	featureset_nnn = [ (id , features(text,stopwords)) for id, text in make_req(listing_ids, 0,200)]
	#ddd = ie_preprocess(ddd.lower())
	#featureset_nnn.append((0000,features(ddd,stopwords)))

	rst = {}
	rst["total"] = 0
	rst["passed"] = 0
	rst["failed"] = 0
	rst["passed_listings"] = []
	rst["failed_listings"] = []
	for id, n in featureset_nnn :
		rst["total"] += 1
		print classifier.classify(n)
		if not classifier.classify(n):
			rst["passed"] = rst["passed"] + 1
			rst["passed_listings"].append(id)
		else:
			rst["failed"] = rst["failed"] + 1
			rst["failed_listings"].append(id)
			#print n
	print "result", rst



def make_req(listing_ids, start=0, rows=200):
    payload = {'q': '*:*', "wt": "json"}
    payload["fq"] = ["DOCUMENT_TYPE:DIRTY_LISTING"]
    #payload["fq"] += ["LISTING_POSTED_DATE:[2016-08-01T00:00:00Z TO *]", "LISTING_STATUS:RAW"
    #, "UNIT_TYPE:Apartment"]

    #payload["fq"] += ["LISTING_CATEGORY:Primary"]

    #print "listings: ", listing_ids
    if listing_ids :
    	payload["fq"] += ["LISTING_ID: (%s)" %( " OR ".join(listing_ids) ,) ]

    #payload["fq"].append("LISTING_ID:2206753")
    print payload
    
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
    print docs
    print
    sent = []
    for doc in docs:
    	desc = doc["LISTING_DESCRIPTION"]
    	desc = remove_tags(desc)
    	desc = desc.lower()
    	listing_id = doc["LISTING_ID"]
    	s = ie_preprocess(desc)
    	sent.append((listing_id ,s))
    	#print s
    return sent


if __name__ == '__main__':
	print  sys.argv[1:]
	listing_ids = sys.argv[1:]
	main(ddd, listing_ids)
