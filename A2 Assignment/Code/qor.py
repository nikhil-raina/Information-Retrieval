import sys
import time as t
from index import read_lookup, read_index_file, ordered_index_dictionary

"""
Search function that performs the document-at-a-time scoring for the query being entered.
It only matches those terms from the query that are in the documents.
@:param: query: the query to be searched for
@:param: inverted_list: the list of keywords
"""
def search(query, inverted_list):
    document_score = dict()
    for q in query:
        for document_ID in inverted_list[q].keys():
            if document_ID in document_score.keys():
                document_score[document_ID] += inverted_list[q][document_ID]
            else:
                document_score[document_ID] = inverted_list[q][document_ID]
    return ordered_index_dictionary(document_score, True)


"""
Method to run the QOR program
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