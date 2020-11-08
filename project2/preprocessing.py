from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from string import punctuation
import re
import json
import math

STOPWORDS = ['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", "you've", "you'll", 
            "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers',
            'herself', 'it', "it's", 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 
            'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have',
            'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
            'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 
            'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
            'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some',
            'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't",
            'should', "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn', "didn't",
            'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn',
            "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won', "won't", 
            'wouldn', "wouldn't"]

#using utf-8 format as the html files where encoded in that and has special chars that require it to be utf-8

def loadFile():
    documents = {} #key=doc; value=document
    htmlIDs = {}
    transcriptFile = open('p2-data/All Transcripts - My Little Pony Friendship is Magic Wiki.html', encoding='utf-8')
    soup = BeautifulSoup(transcriptFile.read(), 'html.parser')
    transcriptFile.close()
    tags = soup.find(id='mw-content-text').find('p').contents
    currDoc = None
    i=0
    while i < len(tags):
        if tags[i] != '\n':
            if tags[i].name == 'h2':
                currDoc = tags[i].text.strip()
                htmlID = tags[i].attrs['id']
                htmlIDs[currDoc] = htmlID
                try:
                    documents[currDoc].append(currDoc)
                except:
                    documents[currDoc] = [currDoc]
            elif currDoc != None:
                if tags[i].name == 'table':
                    attr =  tags[i].attrs
                    if 'class' in  attr.keys() and attr['class'] == 'navbox':
                        break
                text = tags[i].text.strip()
                if text:
                    documents[currDoc].append(text)
        i += 1
    return documents, htmlIDs



def sentenceSelection( docIds, query):
    global docs
    termFrequency = json.load(open('tfidf/tf.json','r', encoding='utf-8'))
    docIds = json.load(open('tfidf/docIds.json','r',encoding='utf-8'))
    ps = PorterStemmer()
    documentSignificance = {} 
    for docId in docIds:
        docName = docIds[docId]
        sd = len(docs[docName])
        if sd < 25:
            limit = 7 + (0.1*(sd-40))
        elif sd <= 40:
            limit = 7
        else:
            limit = 7 - (0.1*(25-sd))

        bestSentence = [None, None, None]
        s = ''
        docs[docName] = ' '.join(docs[docName]).split('.')
        for sentence in docs[docName]:
            tokens = re.split(r'\s+|['+punctuation+r']\s*', sentence.strip().lower())
            tokens = [ps.stem(k) for k in tokens]
            if not any(item in tokens for item in query):
                continue
            sigWords = []
            for token in tokens:
                if token == '':
                    continue
                if termFrequency[docId][token] >= limit:
                    sigWords.append(1)
                else:
                    sigWords.append(0)
            try:
                currSentence = ([sum(sigWords), sigWords.index(1), len(sigWords) - 1 - sigWords[::-1].index(1)])
            except:
                continue
            if bestSentence[1] == None or bestSentence[1] < currSentence[1]:
                bestSentence = currSentence
                s = re.split(r'\s+|['+punctuation+r']\s*', sentence.strip())
                s = ' '.join(s) + '\n'
        documentSignificance[docId] = s
    return documentSignificance

def indexDocsTdidf(docs, htmlIDs):
    ps = PorterStemmer()
    currDocId = 0
    docIds = {}
    termFrequency = {}
    invertedIndex = {}
    for docName in docs.keys():
        wordFrequency = {}
        docIds[currDocId] = docName
        for line in docs[docName]:
            tokens = re.split(r'\s+|['+punctuation+r']\s*', line.strip())
            for token in tokens:
                token = ps.stem(token.lower())
                if token != '':
                    try:
                        wordFrequency[token]+=1.0
                    except:
                        wordFrequency[token] = 1.0
                    try:
                        invertedIndex[token].add(currDocId)
                    except:
                        invertedIndex[token] = {currDocId}
        termFrequency[currDocId] = wordFrequency
        currDocId+=1
    invertedIndex = {k:list(v) for k,v in invertedIndex.items()}
    inverseDocFrequency = {k: math.log(len(docIds)/(len(v))) for k,v in invertedIndex.items()}        
    tf_idf = {}
    normalization = {}
    for id in docIds.keys():
        for term in termFrequency[id].keys():
            try:
                tf_idf[id][term] = (math.log(termFrequency[id][term]) + 1.0) * inverseDocFrequency[term]
                normalization[id] += tf_idf[id][term]**2
            except:
                tf_idf[id] = {term:termFrequency[id][term] * inverseDocFrequency[term]}
                normalization[id] = tf_idf[id][term]**2

    normalization = {k: (v**(1/2)) for k,v in normalization.items()}
    

    for id in docIds.keys():
        tf_idf[id] = { k: (v/normalization[id]) for k,v in tf_idf[id].items()}

    out = open('tfidf/tf.json','w', encoding='utf-8')
    json.dump(termFrequency, out,ensure_ascii=False)
    out.close()
    out = open('tfidf/idf.json','w',encoding='utf-8')
    json.dump(inverseDocFrequency,out,ensure_ascii=False)
    out.close()
    out = open('tfidf/invertedIndex.json','w',encoding='utf-8')
    json.dump(invertedIndex,out,ensure_ascii=False)
    out.close()
    out = open('tfidf/tf_idf.json','w',encoding='utf-8')
    json.dump(tf_idf,out,ensure_ascii=False)
    out.close()
    out = open('tfidf/docIds.json','w',encoding='utf-8')
    json.dump(docIds,out,ensure_ascii=False)
    out.close()
    out = open('tfidf/htmlIds.json','w',encoding='utf-8')
    json.dump(htmlIDs,out,ensure_ascii=False)
    out.close()

def indexDocsBM25(docs, htmlIDs):
    k1,  b  = 1.0, 0.75
    ps = PorterStemmer()
    currDocId = 0
    docIds = {}
    termFrequency = {}
    invertedIndex = {}
    docLengths = {}
    totalDoclengths = 0
    for docName in docs.keys():
        wordFrequency = {}
        docIds[currDocId] = docName
        docLength = 0
        for line in docs[docName]:
            tokens = re.split(r'\s+|['+punctuation+r']\s*', line.strip())
            for token in tokens:
                token = ps.stem(token.lower())
                if token != '':
                    try:
                        wordFrequency[token]+=1.0
                    except:
                        wordFrequency[token] = 1.0
                    try:
                        invertedIndex[token].add(currDocId)
                    except:
                        invertedIndex[token] = {currDocId}
                    docLength+=1
        docLengths[currDocId] = docLength
        totalDoclengths += docLength
        termFrequency[currDocId] = wordFrequency
        currDocId+=1
    docLengths = {k:(v/totalDoclengths) for k,v in docLengths.items()}
    Kvals = {k: k1*((1-b)+(v*b)) for k,v in docLengths.items()}
    B25Score = {}
    for docId in docIds.keys():
        B25Score[docId] = {k: (math.log((len(docIds) - len(invertedIndex[k]) + 0.5 )/((len(invertedIndex[k]) + 0.5)))*
                                        (((k1+1.0)*v)/(0.0+Kvals[docId] + v))) for k, v in termFrequency[docId].items()}

    out = open('BM25/score.json','w', encoding='utf-8')
    json.dump(B25Score, out,ensure_ascii=False)
    out.close()
    out = open('BM25/htmlIds.json','w', encoding='utf-8')
    json.dump(htmlIDs, out,ensure_ascii=False)
    out.close()

docs, htmlIDs = loadFile()

if __name__ == "__main__":
    indexDocsTdidf(docs, htmlIDs)
    indexDocsBM25(docs, htmlIDs)    
    pass

