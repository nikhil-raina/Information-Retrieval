from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from string import punctuation
import re
import json
import math



#using utf-8 format as the html files where encoded in that and has special chars that require it to be utf-8

#loads .html file and separates all the documents
def loadFile():
    documents = {} #key=doc; value=document
    htmlIDs = {} #stores the tag ids for document headers in the HTML file in order to create links to the document
    
    transcriptFile = open('p2-data/All Transcripts - My Little Pony Friendship is Magic Wiki.html', encoding='utf-8')
    soup = BeautifulSoup(transcriptFile.read(), 'html.parser')
    transcriptFile.close()
    # finds the tag with id = 'mw-content-text', then finds p tag in it and gets it's contents
    tags = soup.find(id='mw-content-text').find('p').contents
    currDoc = None
    i=0
    while i < len(tags):
        #skip tag that only have new lines
        if tags[i] != '\n':
            #check if the current tag is h2, i.e. the title of the document
            if tags[i].name == 'h2':
                #strip the string of extra spaces, tabs and new lines 
                currDoc = tags[i].text.strip()
                #access the id attribute of the tag, this is the title of the document
                htmlID = tags[i].attrs['id']
                htmlIDs[currDoc] = htmlID
                #append the title to the document.
                try:
                    documents[currDoc].append(currDoc)
                except:
                    documents[currDoc] = [currDoc]
            
            elif currDoc != None:
                #the documents end with a table, so checks if the correct table tag is reached, 
                # if it is reached then all the documents have been read
                if tags[i].name == 'table':
                    #checks if the class attribute is 'navbox'
                    attr =  tags[i].attrs
                    if 'class' in  attr.keys() and attr['class'] == 'navbox':
                        break
                #reads the line and if it's not null adds it to the current document.
                text = tags[i].text.strip()
                if text:
                    documents[currDoc].append(text)
        i += 1
    return documents, htmlIDs


#select sentences to show in summary for the documents in doc_ids and words in query
def sentenceSelection( docIds, query):
    global docs
    #loading the term frequency
    termFrequency = json.load(open('tfidf/tf.json','r', encoding='utf-8'))
    #loading the document ids
    docIds = json.load(open('tfidf/docIds.json','r',encoding='utf-8'))
    #stemmer
    ps = PorterStemmer()
    #stores sentences for each document in docIds
    documentSignificance = {} 
    
    #loops through all the documents
    for docId in docIds:
        #get the document name
        docName = docIds[docId]

        #separating sentences in the document 
        docs[docName] = ' '.join(docs[docName]).split('.')

        #document length
        sd = len(docs[docName])
        #limit for the word to be significant
        if sd < 25:
            limit = 7 + (0.1*(sd-40))
        elif sd <= 40:
            limit = 7
        else:
            limit = 7 - (0.1*(25-sd))

        bestSentence = None
        s = ''
        
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
                currSentence = sum(sigWords)
            except:
                continue
            if bestSentence == None or bestSentence < currSentence:
                bestSentence = currSentence
                s = sentence.replace('\n',' ') 
        documentSignificance[docId] = s
    return documentSignificance

#creates index files for td.idf
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

#creates index files for BM25
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

