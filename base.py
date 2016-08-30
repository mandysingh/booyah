from nltk.corpus import conll2000
import nltk, re, pprint
from BeautifulSoup import BeautifulSoup
import requests


def remove_tags(raw_text):
    return BeautifulSoup(raw_text).text


def ie_preprocess(document):
    sentences = nltk.sent_tokenize(document)
    #print sentences
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    #print sentences
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences


def print_analysis(doc):
    doc = remove_tags(doc)
    sentences = ie_preprocess(doc)
    return sentences

def make_req():
    payload = {'q': '*:*', "wt": "json"}
    payload["fq"] = ["DOCUMENT_TYPE:DIRTY_LISTING", "LISTING_POSTED_DATE:[2016-08-01T00:00:00Z TO *]", "LISTING_STATUS:Active"
    , "UNIT_TYPE:Apartment", "LISTING_CATEGORY:Primary"]

    #payload["fq"].append("LISTING_ID:2206753")

    payload["rows"] = 200
    payload["fl"] = ["LISTING_DESCRIPTION","LISTING_ID"]
    host = "http://localhost:8983/solr/collection_mp/select"
    
    req = requests.get(host, params=payload)
    docs = req.json()["response"]["docs"]

    for doc in docs:
        print doc["LISTING_ID"]
        print print_analysis(doc["LISTING_DESCRIPTION"])
