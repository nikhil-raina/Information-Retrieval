import json 
import sys
import time
from nltk.stem import PorterStemmer
import preprocessing
import create_html_file


#loading json files created by preprocessing.py
tf_idf = json.load(open('tfidf/tf_idf.json','r', encoding='utf-8'))
BM25 = json.load(open('BM25/score.json','r', encoding='utf-8'))
invertedIndex = json.load(open('tfidf/invertedIndex.json','r', encoding='utf-8'))
docIds = json.load(open('tfidf/docIds.json','r', encoding='utf-8'))
htmlId = json.load(open('tfidf/htmlIds.json','r', encoding='utf-8'))
#stemmer 
ps = PorterStemmer()

#takes in query and scores and then ranks the 
def search(query, scores):
    
    #log start time
    start_time = time.time()
    
    #stem the query words
    query_stem = [ps.stem(x.lower()) for x in query]

    doc_score = {}
    #loop through each query word to find the score for each term
    for term in query_stem:
        try:
            #loop through all the docs that have the term
            for doc_id in invertedIndex[term]:
                doc_id = str(doc_id)
                #add the score for that (doc, term)
                try:
                    doc_score[doc_id] += scores[doc_id][term]
                except:
                    doc_score[doc_id] = scores[doc_id][term]
        except:
            continue

    #sort the doc_ids with respect to the scores 
    doc_score = [k for k, v in sorted(doc_score.items(), key = lambda item: item[1], reverse=True)]

    #log the end time
    end_time = time.time()

    #get the summary for the ranked documents
    summary = preprocessing.sentenceSelection(doc_score[0:10], query_stem)
    
    finalResult = []
    #create a data structure to return the results
    for doc_id in doc_score[0:10]:
        document = {}
        document['title'] = docIds[doc_id]
        document['summary'] = summary[doc_id]
        document['link'] = htmlId[docIds[doc_id]]
        finalResult.append(document)
    
    print('Execution Time: ', end_time-start_time)
    print('Total unique matched documents: ', len(doc_score))

    #print the result to the console
    # for doc in finalResult:
    #     print(doc['title'] + '\t\t' + doc['summary']+'\t\t'+doc['link'])
    create_html_file.write_html(open( 'html/'+ '_'.join(query) + '_'+sys.argv[1] + '.html', 'w'), {'query': query, 'result': finalResult})
    return {'query': query, 'result': finalResult}


#main
if __name__ == "__main__":
    # check input arguments 
    # if len(sys.argv) < 2:
    #     print('Usage : python project2.py <modelType> query')
    #     print('modelType: tfidf | BM25')
    #     exit()
    # #check which model to test.
    # if sys.argv[1] == 'tfidf':
    #     query = sys.argv[2:]
    #     doc_score = search(query, tf_idf)
    # else:
    #     query = sys.argv[2:]
    #     doc_score = search(query, BM25)    
    sys.argv= ['', 'BM25']
    
    doc_score = search(['Sounds', 'of', 'Silence'], BM25)
    doc_score = search([ 'rarity','manehattan'], BM25)
    doc_score = search(['Twenty', 'five', 'different', 'types', 'of', 'tricks', 'and', 'counting'], BM25)


    # output the result to a json file.
    # with open('result.json', 'w',  encoding='utf-8') as result_file:
    #     json.dump(doc_score, result_file)

    
    