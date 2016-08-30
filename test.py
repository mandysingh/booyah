#from nltk.corpus import

from nltk.corpus import conll2000
import nltk, re, pprint
from BeautifulSoup import BeautifulSoup
import requests


def remove_tags(raw_text):
    return BeautifulSoup(raw_text).text

document = '''
\nCherry Residency by Sanskruti Builders, located in Nala Sopara, Mumbai brings you a spacious 1 bedroom apartment with 1 bathroom.\nCurrently in Completed status, this apartment is of 645 sqft. and per sqft price is Rs. 3,721.\n\nThe total price of the property is Rs. 24.00 Lacs.\n\nKitchen has Vitrified Tiles, Glazed Tiles Dado up to 2 Feet Height Above Platform and Granite Platform with Stainless Steel Sink. Toilets have Ceramic Tiles, Full Height Designer Tiles, Concealed Plumbing and CP Fittings. Points have Master Bedroom, Other Bedroom, Living, Dining, Kitchen and Hall. Balcony and Toilets have Ceramic Tiles. Kitchen, Living/Dining, Master Bedroom and Other Bedroom have Vitrified Tiles. Exterior has Acrylic Paint. Windows have Powder Coated Aluminium Sliding, Wiring has Concealed Copper Wiring and Switches has Modular Switches.\n\nThe project has Car Parking, Power Backup, Lift Available, Rain Water Harvesting, 24 X 7 Security, Vaastu Compliant, Children's play area, Multipurpose Room, Intercom, Shopping Mall and School. It also has Hospital, ATM, Others, Swimming Pool, Landscaped Gardens, Indoor Games, Gymnasium, Swimming Pool, Landscaped Gardens and Indoor Games.\n

'''

doc2 = '''
Loan facility available 80% on this flat.\nLuxurious 1 king size bedroom with 1 balcony and 1 bathroom.\nNew and Front side flat.\nUnder Construction Property.\nProperty on 1st floor.\nTotal 5 floors in building. \nSemi furnished property.\nNext to crossing Republik.\nWith car parking, lift & power backup. \nSeparate drawing room & dining room.\nModular kitchen. \nGated society.\n\nProperty on 30 ft wide road.\nGood quality wood work.\nVitrified tiles flooring.\nAttractive electric fitting.\nWith still car parking\nWith good location\nFriends enclave in sector 4, greater noida west.\nNear by radha swami aashram.\nNear by McDonald & pizza hut.\nNear by Varandavan Hospital, Modern public school in 2 min.\nNear by Galaria market in 1 km, A.B.S College in 2 km, \t\t\nNear by Gaur City.
'''


def find_bhk(text):
    return re.search('(\d+)[\s]{,3}(bedrooms?|bhk|BHK|Bhk)', doc3).group(1)


def ie_preprocess(document):
    sentences = nltk.sent_tokenize(document)
    #print sentences
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    #print sentences
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences


def ner_tag(sentences):
    for sent in sentences:
        print nltk.ne_chunk(sent)




    
grammar = r"""
  NP: {<CD|DT|JJ|NN.*>+}          # Chunk sequences of DT, JJ, NN
  PP: {<IN><NP>}               # Chunk prepositions followed by NP
  VP: {<VB.*><NP|PP|CLAUSE>+$} # Chunk verbs and their arguments
  CLAUSE: {<NP><VP>}           # Chunk NP, VP
  """
cp = nltk.RegexpParser(grammar)


grammar_project = r'''
    NP: ^<``>?<DT>?<JJ>?{<NNP.*>+}<V.*>
'''
cp_project = nltk.RegexpParser(grammar_project)

def chunk(sentences):
    #print sentences
    near_by = []
    for sent in sentences:
        # filter near by sentences
        is_near = [(word.lower(), index) for index,(word,pos) in enumerate(sent) if pos == 'IN' and word.lower() in {'near', 'behind'}]
        #print is_near
        if not is_near:
            continue
        else:
            sent = sent[is_near[0][1]:]
        parsed_sent = cp.parse(sent)
        nn = extract_near(parsed_sent)
        #print nn
        near_by += nn
    print near_by


def chunk_project(sentences):
    #print sentences
    all_chunks = []
    for sent in sentences:
        all_chunks += extract_near(cp_project.parse(sent))
    return all_chunks


def extract_near(tree):
    siblings = []
    nps = extract_np(tree)
    for np in nps:
        siblings.append(extract_nn(np))
    return siblings


def extract_np(tree):
    #print "np ", tree
    return list(tree.subtrees(filter=lambda x: x.label() =='NP'))


def extract_nn(tree):
    #print "nn ", tree
    return " ".join([t[0] if t[1].startswith('') else "" for t in tree.leaves() ])

#ie_preprocess(document)


def print_nearby(doc):
    doc = remove_tags(doc)
    sentences = ie_preprocess(doc)
    #chunk(sentences)
    chunked = chunk_project(sentences)
    if chunked:
        print chunked



def make_req():
    payload = {'q': '*:*', "wt": "json"}
    payload["fq"] = ["DOCUMENT_TYPE:DIRTY_LISTING", "LISTING_POSTED_DATE:[2016-08-01T00:00:00Z TO *]", "LISTING_STATUS:Active"
    , "UNIT_TYPE:Apartment", "LISTING_CATEGORY:Primary"]

    #payload["fq"].append("LISTING_ID:2206753")

    payload["rows"] = 200
    payload["fl"] = ["LISTING_DESCRIPTION","LISTING_ID"]
    host = "http://localhost:8983/solr/collection_mp/select"
    #q=*:*&fq=DOCUMENT_TYPE:DIRTY_LISTING&fq=LISTING_POSTED_DATE:[2016-08-01T00:00:00Z TO *]&fq=LISTING_STATUS:Active&fq=UNIT_TYPE:Apartment&fq=LISTING_CATEGORY:Primary
    #&sort=LISTING_QUALITY_SCORE desc, LISTING_SELLER_COMPANY_SCORE desc&rows=2000&fl=LISTING_DESCRIPTION&wt=json
    req = requests.get(host, params=payload)
    docs = req.json()["response"]["docs"]

    for doc in docs:
        desc = doc["LISTING_DESCRIPTION"]
        print doc["LISTING_ID"]
        print_nearby(desc)

