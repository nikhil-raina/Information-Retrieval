import json 
import sys
import time
from nltk.stem import PorterStemmer


tf_idf = json.load(open('tfidf/tf_idf.json'))
BM25 = json.load(open('BM25/score.json'))
invertedIndex = json.load(open('tfidf/invertedIndex.json'))
docIds = json.load(open('tfidf/docIds.json'))
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
    doc_score = {k : v for k, v in sorted(doc_score.items(), key = lambda item: item[1], reverse=True)} 
    print('Execution Time: ', time.time()-start_time)
    print('Total unique matched documents: ', len(doc_score))
    count = 0
    for doc_id in doc_score.keys():
        if count == 10:
            exit()
        print(str(doc_id) + ' ' + docIds[str(doc_id)])
        count+=1
    return doc_score


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage : python project2.py <modelType> query')
        print('modelType: tfidf | BM25')
        exit()
    print(sys.argv)
    if sys.argv[1] == 'tfidf':
        query = sys.argv[2:]
        doc_score = search(query, tf_idf)
    else:
        query = sys.argv[2:]
        doc_score = search(query, BM25)    
    
    