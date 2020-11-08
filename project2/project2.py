import json 
import sys
import time
from nltk.stem import PorterStemmer
import preprocessing

tf_idf = json.load(open('tfidf/tf_idf.json','r', encoding='utf-8'))
BM25 = json.load(open('BM25/score.json','r', encoding='utf-8'))
invertedIndex = json.load(open('tfidf/invertedIndex.json','r', encoding='utf-8'))
docIds = json.load(open('tfidf/docIds.json','r', encoding='utf-8'))
htmlId = json.load(open('tfidf/htmlIds.json','r', encoding='utf-8'))
ps = PorterStemmer()

def search(query, scores):
    start_time = time.time()
    query = [ps.stem(x.lower()) for x in query]
    doc_score = {}
    for term in query:
        try:
            for doc_id in invertedIndex[term]:
                doc_id = str(doc_id)
                try:
                    doc_score[doc_id] += scores[doc_id][term]
                except:
                    doc_score[doc_id] = scores[doc_id][term]
        except:
            continue
    doc_score = [k for k, v in sorted(doc_score.items(), key = lambda item: item[1], reverse=True)]
    summary = preprocessing.sentenceSelection(doc_score, query)
    finalResult = []
    for doc_id in doc_score:
        document = {}
        document['title'] = docIds[doc_id]
        document['summary'] = summary[doc_id]
        document['link'] = htmlId[docIds[doc_id]]
        finalResult.append(document)

    print('Execution Time: ', time.time()-start_time)
    print('Total unique matched documents: ', len(doc_score))
    count = 0
    for doc in finalResult:
        if count == 10:
            exit()
        print(doc['title'] + '\t' + doc['summary']+'\t'+doc['link'])
        count+=1    
    return finalResult


if __name__ == "__main__":
    # if len(sys.argv) < 2:
    #     print('Usage : python project2.py <modelType> query')
    #     print('modelType: tfidf | BM25')
    #     exit()    
    # if sys.argv[1] == 'tfidf':
    #     query = sys.argv[2:]
    #     doc_score = search(query, tf_idf)
    # else:
    #     query = sys.argv[2:]
    #     doc_score = search(query, BM25)    

    doc_score = search(['Rarity' ,'manehattan'], BM25)

    
    