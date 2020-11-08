from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from string import punctuation
import re
import json
import math



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
                documents[currDoc] = [currDoc]
            elif currDoc != None:
                if tags[i].name == 'table':
                    attr =  tags[i].attrs
                    if 'class' in  attr.keys() and attr['class'] == 'navbox':
                        break
                documents[currDoc].append(tags[i].text)
        i += 1
    return documents, htmlIDs


def indexDocs():
    docs, htmlIDs = loadFile()
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
indexDocs()
