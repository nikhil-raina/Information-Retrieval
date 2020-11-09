from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from string import punctuation
import re
import json
import math

STOPWORDS = ['a', 'about', 'above', 'after', 'again', 'against', 'ain', 'all', 'am', 'an', 'and', 
            'any', 'are', 'aren', "aren't", 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 
            'between', 'both', 'but', 'by', 'can','couldn', "couldn't", 'd', 'did', 'didn', "didn't", 'do', 'does',
            'doesn', "doesn't", 'doing', 'don', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 'further',
            'had', 'hadn', "hadn't", 'has', 'hasn', "hasn't", 'have', 'haven', "haven't", 'having', 'he',
            'her', 'here','hers', 'herself', 'him', 'himself', 'his', 'how','i','if', 'in', 'into', 'is', 'isn',
            "isn't", 'it', "it's", 'its', 'itself', 'just', 'll', 'm', 'ma', 'me', 'mightn', "mightn't",
            'more', 'most', 'mustn', "mustn't", 'my', 'myself', 'needn', "needn't", 'no', 'nor', 'not', 'now',
            'o', 'of', 'off', 'on', 'once', 'only', 'or', 'other','our', 'ours',
            'ourselves', 'out', 'over', 'own', 're', 's', 'same', 'shan', "shan't", 'she',"she's", 'should',
            "should've", 'shouldn', "shouldn't", 'so', 'some', 'such', 't', 'than', 'that', "that'll",
            'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there','these', 'they',
            'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 've', 'very', 'was', 'wasn', "wasn't", 'we',
            'were', 'weren', "weren't", 'what','when','where','which', 'while', 'who','whom', 'why', 'will',
            'with', 'won', "won't",'wouldn', "wouldn't", 'y', 'you', "you'd", "you'll", "you're", "you've",
            'your', 'yours', 'yourself', 'yourselves']


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

        #initial best sentence
        bestSentence = None
        s = ''
        
        #loop through all the sentences to find the best one 
        for sentence in docs[docName]:
            #split the sentence on space and punctuations and covert them to lower case
            tokens = re.split(r'\s+|['+punctuation+r']\s*', sentence.strip().lower())
            #stem the tokens
            tokens = [ps.stem(k) for k in tokens]
            #check if any query keyword in the tokens
            if not any(item in tokens for item in query):
                continue
            #finds the significant word
            sigWords = []
            #loop through the token
            for token in tokens:
                if token == '' and token not in STOPWORDS:
                    continue
                #check if the term frequency for the token is greater than limit
                if termFrequency[docId][token] >= limit:
                    sigWords.append(1)
                else:
                    sigWords.append(0)
            try:
                #find the number of significant words
                currSentence = sum(sigWords)
            except:
                continue
            #check if this is the best number of significant words
            if bestSentence == None or bestSentence < currSentence:
                bestSentence = currSentence
                s = sentence.replace('\n',' ') 
        documentSignificance[docId] = s
    return documentSignificance

#creates index files for td.idf
def indexDocsTdidf(docs, htmlIDs):
    #stemmer
    ps = PorterStemmer()
    # document Id counter
    currDocId = 0
    #dictonary for document id to document title
    docIds = {}
    #dictionary for term frequency that maps docId -> terms -> frequency
    termFrequency = {}
    #dictionary for inverted index that maps term -> list of docIds 
    invertedIndex = {}
    #loop through documents
    for docName in docs.keys():
        #term frequency for this document
        wordFrequency = {}
        #store the docId -> docName
        docIds[currDocId] = docName
        #loop through the lines in document
        for line in docs[docName]:
            #split the line into tokens
            tokens = re.split(r'\s+|['+punctuation+r']\s*', line.strip())
            #loop through the tokens
            for token in tokens:
                #convert the token to lower case and then stem them
                token = ps.stem(token.lower())

                if token != '':
                    #add the occurrence of the token
                    try:
                        wordFrequency[token]+=1.0
                    except:
                        wordFrequency[token] = 1.0
                    #add the document id to inverted index for the term
                    try:
                        invertedIndex[token].add(currDocId)
                    except:
                        invertedIndex[token] = {currDocId}
        #store the term frequency of the document
        termFrequency[currDocId] = wordFrequency
        currDocId+=1
    #coverts the sets in inverted list to lists
    invertedIndex = {k:list(v) for k,v in invertedIndex.items()}
    #calculate the inverse doc frequency
    inverseDocFrequency = {k: math.log(len(docIds)/(len(v))) for k,v in invertedIndex.items()}
    #dictionary to store tf.idf       
    tf_idf = {}
    #normalization vector
    normalization = {}
    #loop through all the documents
    for id in docIds.keys():
        #loop through all the unique terms in the document
        for term in termFrequency[id].keys():
            try:
                #calculated the tf.idf for (doc, term) pair
                tf_idf[id][term] = (math.log(termFrequency[id][term]) + 1.0) * inverseDocFrequency[term]
                normalization[id] += tf_idf[id][term]**2
            except:
                #calculated the tf.idf for (doc, term) pair
                tf_idf[id] = {term:termFrequency[id][term] * inverseDocFrequency[term]}
                normalization[id] = tf_idf[id][term]**2
    #calculating the normalization value 
    normalization = {k: (v**(1/2)) for k,v in normalization.items()}
    
    #calculating the normalized tf.idf 
    for id in docIds.keys():
        tf_idf[id] = { k: (v/normalization[id]) for k,v in tf_idf[id].items()}

    #outputing the json files
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
    k1,  b  = 1.2, 0.75
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

