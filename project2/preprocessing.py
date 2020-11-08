from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from string import punctuation
import re
import json
import math


alpha = 0.3


#using utf-8 format as the html files where encoded in that and has special chars that require it to be utf-8

def loadFile():
    documents = {} #key=doc; value=document
    transcriptFile = open('project2/p2-data/All Transcripts - My Little Pony Friendship is Magic Wiki.html', encoding='utf-8')
    soup = BeautifulSoup(transcriptFile.read(), 'html.parser')
    transcriptFile.close()
    tags = soup.find(id='mw-content-text').find('p').contents
    currDoc = None
    i=0
    while i < len(tags):
        if tags[i] != '\n':
            if tags[i].name == 'h2':
                currDoc = tags[i].text.strip()
                documents[currDoc] = [currDoc]
            elif currDoc != None:
                if tags[i].name == 'table':
                    attr =  tags[i].attrs
                    if 'class' in  attr.keys() and attr['class'] == 'navbox':
                        break
                documents[currDoc].append(tags[i].text)
        i += 1
    return documents


def indexDocs():
    docs = loadFile()
    ps = PorterStemmer()
    currDocId = 0
    docIds = {}
    termFrequency = {}
    invertedIndex = {}
    for docName in docs.keys():
        wordFrequency = {}
        wordsInDoc = 0.0
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
                    wordsInDoc+=1.0
        for word in wordFrequency.keys():
            wordFrequency[word] /= wordsInDoc 
        termFrequency[currDocId] = {'doc':wordsInDoc, 'terms':wordFrequency}

        currDocId+=1
    invertedIndex = {k:list(v) for k,v in invertedIndex.items()}
    inverseDocFrequency = {k: math.log(len(docIds)/(len(v)+1)) for k,v in invertedIndex.items()}        
    tf_idf = {}
    for id in docIds.keys():
        for term in termFrequency[id]['terms'].keys():
            try:
                tf_idf[id][term] = termFrequency[id]['terms'][term] * inverseDocFrequency[term]
            except:
                tf_idf[id] = {term:termFrequency[id]['terms'][term] * inverseDocFrequency[term]}
            if term not in [ ps.stem(token) for token in docIds[id].lower().split()]:
                tf_idf[id][term] *= alpha
    out = open('tf.json','w', encoding='utf-8')
    json.dump(termFrequency, out,ensure_ascii=False)
    out.close()
    out = open('idf.json','w',encoding='utf-8')
    json.dump(inverseDocFrequency,out,ensure_ascii=False)
    out.close()
    out = open('invertedIndex.json','w',encoding='utf-8')
    json.dump(invertedIndex,out,ensure_ascii=False)
    out.close()
    out = open('tf_idf.json','w',encoding='utf-8')
    json.dump(tf_idf,out,ensure_ascii=False)
    out.close()
    out = open('docIds.json','w',encoding='utf-8')
    json.dump(docIds,out,ensure_ascii=False)
    out.close()
indexDocs()
