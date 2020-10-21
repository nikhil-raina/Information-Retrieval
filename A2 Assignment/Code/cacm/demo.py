from os import walk as w
import re
from string import punctuation


"""
Method indexes all the files to form the inverted list.
Inverted list: 
    {
        word: {}
    }
"""
def indexing(root_folder, document_file_dictionary, document_title_dictionary, inverted_list):
    TAG = re.compile('<.*?>')
    for document_id in document_file_dictionary.keys():
        file_name = document_file_dictionary[document_id]
        html_file = open(root_folder + '/' + file_name)
        clean_text = re.sub(TAG, '', html_file.read())
        linelst = clean_text.split('\n')
        for line in linelst:
            if line != '':
                document_title_dictionary[document_id] = line.strip()
                break
        tokens = re.split(r'\s+|[' + punctuation + r']\s*', clean_text)

        html_file.close()
        for token in tokens:
            if not token:
                continue
            if token.lower() in inverted_list.keys():
                if document_id in inverted_list[token].keys():
                    inverted_list[token][document_id] += 1
                else:
                    inverted_list[token][document_id] = 1
            else:
                inverted_list[token] = {}
                inverted_list[token][document_id] = 1
        return inverted_list


"""
Method that gathers all the files in the root_folder directory and stores them separately as values in a dictionary
with the keys as the index positions of those files.

@:param: root_folder: the directory where the files will be searched for
@:param: book: the dictionary that will contain the numbered files.
"""
def create_doc_list(root_folder, document_file_dictionary):
    doc_id = 0
    for (root_folder_name, directories, files) in w(root_folder):
        files.sort()
        for file in files:
            document_file_dictionary[doc_id] = file
            doc_id += 1


"""
"""
def doc_lookup(document_file_dictionary, document_title_dictionary):
    doc_file = open('lookup.tsv', 'w')
    for doc_id in document_file_dictionary.keys():
        doc_file.write(str(doc_id) + '\t' +
                       document_file_dictionary[doc_id] + '\t' +
                       document_title_dictionary[doc_id] + '\n')
    doc_file.close()


"""
"""
def write_inverted_index(inverted_list):
    index_file = open('index.tsv', 'w')
    keywords = list(inverted_list.keys())
    keywords.sort()
    for keyword in keywords:
        for doc_id in inverted_list[keyword].keys():
            index_file.write(str(keyword) + '\t' +
                             str(len(inverted_list[keyword].keys())) + '\t' +
                             str(doc_id) + '\t' +
                             str(inverted_list[keyword][doc_id]) + '\n')


"""
Program that first runs the indexing algorithm on the files in the cacm folder 
"""
if __name__ == "__main__":
    root_folder = 'cacm'
    document_file_dictionary = dict()
    document_title_dictionary = dict()
    inverted_list = dict()
    create_doc_list(root_folder, document_file_dictionary)
    indexing(root_folder, document_file_dictionary, document_title_dictionary, inverted_list)
    doc_lookup(document_file_dictionary, document_title_dictionary)
    write_inverted_index(inverted_list)
