import sys
import time as t
from index import read_lookup, read_index_file, ordered_index_dictionary


"""
Search function that performs the document-at-a-time scoring for conjunctive queries being entered.
It matches all the terms in the query to the document.
@:param: query: the query to be searched for
@:param: inverted_list: the list of keywords
"""
def search(query, inverted_list):
    inverted_list_len = dict()
    for q in query:
        inverted_list_len[q] = len(inverted_list[q])
    inverted_list_len = ordered_index_dictionary(inverted_list_len, False)
    document_score = inverted_list[list(inverted_list_len.keys())[0]]
    for q in list(inverted_list_len.keys())[1:]:
        query_1 = document_score
        query_2 = inverted_list[q]
        document_score = dict()
        for document_ID in query_1.keys():
            if document_ID in query_2.keys():
                document_score[document_ID] = query_1[document_ID] + query_2[document_ID]
    return ordered_index_dictionary(document_score, True)


"""
Method to run the QAND program
"""
if __name__ == "__main__":
    start = t.time()
    index_file = 'index.tsv'  # sys.argv[1]
    lookup_file = 'lookup.tsv'  # sys.argv[2]
    query = ['information', 'retrieval', 'compression']  # sys.argv[3:]
    inverted_list = read_index_file(index_file)
    doc_score = dict() if len(query) == 0 else search(query, inverted_list)
    print('Execution Time: ', t.time() - start)
    print('Total unique matched documents: ', len(doc_score), '\n')
    position_counter = 0
    lookup = read_lookup(lookup_file, doc_score.keys())
    for doc_id in doc_score.keys():
        if position_counter == 20:
            break
        print(str(position_counter + 1) + '. ' + str(doc_id) + ' ' + lookup[doc_id] + ' ' + str(doc_score[doc_id]))
        position_counter += 1