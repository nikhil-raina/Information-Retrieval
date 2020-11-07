from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from string import punctuation
import re
import json



def loadFile():
    documents = {} #key=doc; value=document
    transcriptFile = open('project2/p2-data/All Transcripts - My Little Pony Friendship is Magic Wiki.html')
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
    docFrequencies = {}

    for docName in docs.keys():
        wordFrequency = {}
        docFrequency = 0
        docIds[currDocId] = docName
        for line in docs[docName]:
            tokens = re.split(r'\s+|['+punctuation+r']\s*', line.strip())
            tokens = [ps.stem(token) for token in tokens]
            for token in tokens:
                if token != '':
                    if token in wordFrequency.keys():
                        wordFrequency[token]+=1
                    else:
                        wordFrequency[token] = 1
                    docFrequency+=1
        docFrequencies[currDocId] = {'doc':docFrequency, 'words':wordFrequency}

        currDocId+=1
    out = open('test.json','w')
    json.dump(docFrequencies, out)


indexDocs()
