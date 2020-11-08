import json 
import sys
import time
from nltk.stem import PorterStemmer


tf_idf = json.load(open('BM25/score.json'))
invertedIndex = json.load(open('tfidf/invertedIndex.json'))
docIds = json.load(open('tfidf/docIds.json'))
ps = PorterStemmer()

def search(query):
    doc_score = {}
    for term in query:
        try:
            for doc_id in invertedIndex[term]:
                doc_id = str(doc_id)
                try:
                    doc_score[doc_id] += tf_idf[doc_id][term]
                except:
                    doc_score[doc_id] = tf_idf[doc_id][term]
        except:
            continue
    doc_score = {k : v for k, v in sorted(doc_score.items(), key = lambda item: item[1], reverse=True)} 
    return doc_score

if __name__ == "__main__":
    start_time = time.time()
    # if len(sys.argv) < 2:
    #     print('Usage : python dfd.py query')
    #     exit()
    query = [ 'discord']
    query = [ps.stem(x.lower()) for x in query]
    doc_score = search(query)
    print('Execution Time: ', time.time()-start_time)
    print('Total unique matched documents: ', len(doc_score))
    count = 0
    for doc_id in doc_score.keys():
        if count == 15:
            exit()
        print(str(doc_id) + ' ' + docIds[str(doc_id)])
        count+=1