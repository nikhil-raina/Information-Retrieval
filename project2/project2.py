import json 

a = json.load(open('tf_idf.json'))

def search(query):
    try:
        #finding the length of inverted lists for all the query words
        inverted_list_len = []
        for q in query:
            inverted_list_len.append(len(inverted_list[q]))
        zipped = zip(inverted_list_len, query)
        #sorting the query words accoring to the inverted list length.
        query = [x for _,x in sorted(zipped)]
        #using the doc_list for the first query word
        curr_docs = inverted_list[query[0]]
        #looping through all other query words
        for q in query[1:]:
            q1Docs = curr_docs
            q2Docs = inverted_list[q]
            curr_docs = {}
            #checks if both q1 and q2 docs have the documents in them 
            for doc_id in q1Docs.keys():
                if doc_id in q2Docs.keys():
                    curr_docs[doc_id] = q1Docs[doc_id] + q2Docs[doc_id]
        #sorting the documents 
        curr_docs = {k : v for k, v in sorted(curr_docs.items(), key = lambda item: item[1], reverse=True)}    
        return curr_docs    
    except:
        return {}