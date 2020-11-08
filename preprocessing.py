from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from string import punctuation
import re
import json



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
                currDoc = tags[i].text
                documents[currDoc] = []
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
    inverseDocFrequency = {}
    for docName in docs.keys():
        wordFrequency = {}
        wordsInDoc = 0
        docIds[currDocId] = docName
        for line in docs[docName]:
            tokens = re.split(r'\s+|['+punctuation+r']\s*', line.strip())
            for token in tokens:
                token = token.lower()
                if token != '':
                    try:
                        wordFrequency[token]+=1
                    except:
                        wordFrequency[token] = 1
                    try:
                        inverseDocFrequency[token].add(currDocId)
                    except:
                        inverseDocFrequency[token] = {currDocId}
                    wordsInDoc+=1
        termFrequency[currDocId] = {'doc':wordsInDoc, 'term':wordFrequency}
        currDocId+=1
    inverseDocFrequency = {k:len(v) for k,v in inverseDocFrequency.items()}
    out = open('tf.json','w', encoding='utf-8')
    json.dump(termFrequency, out,ensure_ascii=False)
    out.close()
    out = open('idf.json','w',encoding='utf-8')
    json.dump(inverseDocFrequency,out,ensure_ascii=False)
    out.close()
    return termFrequency
indexDocs()
