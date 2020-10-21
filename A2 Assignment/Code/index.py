from os import walk as w
import re
from string import punctuation


"""
Method removes all the html tags from the file and returns a clean final file back
@:param: file: html file
"""
def clean_html(file):
    tag_remover = re.compile('<.*?>')
    final_text = re.sub(tag_remover, '', file)
    return final_text


"""
Method indexes all the files to form the inverted list.
Inverted list: 
    {
        word: {
            doc: word_count
        }
    }
@:param: root_folder: the directory where the files will be searched for
@:param: document_file_dictionary: dictionary that contains the indexed files
"""
def indexing(root_folder, document_file_dictionary):
    document_title_dictionary = dict()
    inverted_list = dict()
    for document_id in document_file_dictionary.keys():
        file_name = document_file_dictionary[document_id]
        html_file = open(root_folder + '/' + file_name)
        text_file = clean_html(html_file.read())
        html_file.close()
        line = text_file.split('\n')
        title_counter = 0
        while line[title_counter] == '':
            title_counter += 1
        title = line[title_counter]
        document_title_dictionary[document_id] = title.strip()
        words = re.split(r'\s+|[' + punctuation + r']\s*', text_file)

        for word in words:
            if not word:
                continue
            word = word.lower()
            if word in inverted_list.keys():
                if document_id in inverted_list[word].keys():
                    inverted_list[word][document_id] += 1
                else:
                    inverted_list[word][document_id] = 1
            else:
                inverted_list[word] = dict()
                inverted_list[word][document_id] = 1
    return document_title_dictionary, inverted_list


"""
Method that gathers all the files in the root_folder directory and stores them separately as values in a dictionary
with the keys as the index positions of those files.
@:param: root_folder: the directory where the files will be searched for
@:param: book: the dictionary that will contain the numbered files.
"""
def document_list_creator(root_folder, document_file_dictionary):
    doc_id = 0
    for (root_folder_name, directories, files) in w(root_folder):
        files.sort()
        for file in files:
            document_file_dictionary[doc_id] = file
            doc_id += 1


"""
Writes the document title and the document file to the lookup.tsv file in the following format:
    document_ID <TAB> document_file_name <TAB> document_title
@:param: document_file_dictionary: dictionary containing the file names
@:param: document_title_dictionary dictionary containing the title of each file
"""
def document_lookup(document_file_dictionary, document_title_dictionary):
    doc_file = open('lookup.tsv', 'w')
    for doc_id in document_file_dictionary.keys():
        doc_file.write(str(doc_id) + '\t' +
                       document_file_dictionary[doc_id] + '\t' +
                       document_title_dictionary[doc_id] + '\n')
    doc_file.close()


"""
Writes the inverted list to the index.tsv file in the following format:
    word <TAB> document_count <TAB> document_ID <TAB> word_count
@:param: inverted_list: the inverted list
"""
def write_inverted_index_to_file(inverted_list):
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
General function that reads the index file and returns the inverted list
@:param: index_file_name: index file name
"""
def read_index_file(index_file_name):
    inverted_list = dict()
    index_file = open(index_file_name, 'r')
    for line in index_file.readlines():
        sequence = line.replace('\n', '').split('\t')
        if sequence[0] in inverted_list:
            inverted_list[sequence[0]][sequence[2]] = int(sequence[3])
        else:
            inverted_list[sequence[0]] = dict()
            inverted_list[sequence[0]][sequence[2]] = int(sequence[3])
    return inverted_list


"""
General function that reads the lookup file and returns the looked up document
@:param: filename: the look up file name
@:param: doc_ids: the ids of all the documents
"""
def read_lookup(filename, doc_ids):
    doc_file = open(filename, 'r')
    doc_lookup = {}
    for line in doc_file.readlines():
        sequence = line.split('\t')
        if sequence[0] in doc_ids:
            doc_lookup[sequence[0]] = sequence[2].replace('\n', '')
    return doc_lookup


"""
General method to order the index dictionary
@:param: document_score: the dictionary to be sorted
@:param: flag: boolean value to decide whether the dictionary should be order in reverse or not
"""
def ordered_index_dictionary(document_score, flag):
    document_tuple_list = sorted(document_score.items(), key=lambda x: x[1], reverse=flag)
    for key, value in document_tuple_list:
        document_score[key] = value
    return document_score

"""
Program that first runs the indexing algorithm on the files in the cacm folder 
"""
if __name__ == "__main__":
    root_folder = 'cacm'
    document_file_dictionary = dict()
    document_list_creator(root_folder, document_file_dictionary)
    document_title_dictionary, inverted_list = indexing(root_folder, document_file_dictionary)
    document_lookup(document_file_dictionary, document_title_dictionary)
    write_inverted_index_to_file(inverted_list)
