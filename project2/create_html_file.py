import json as j


def put_highlight(summary, query):
    start = 0
    new_summary = ''
    temp = summary
    for term in query:
        while summary.lower().find(term.lower()) != -1:
            index = summary.lower().find(term.lower(), start)
            new_summary = new_summary + summary[0:index] + '<span style="background-color:yellow">' + summary[index: index + len(term)] + '</span>'
            summary = summary[index + len(term):]
        if summary.lower().find(term.lower()) == -1:
            new_summary += summary
            summary = new_summary
            new_summary = ''
        else:
            summary = temp

    return summary


def terms_present(query, summary):
    not_present_list = list()
    for terms in query:
        if summary.lower().find(terms.lower()) == -1:
            not_present_list.append(terms)
    return not_present_list


"""
Method that accepts a file writer and a list with some data:
        [
            {
                'title': '',
                'summary': '',
                'link' : ''
            },
            {},
            {},
            .
            .
            .
        ]
"""
def write_html(file, document_list):
    web_page_link = 'All Transcripts - My Little Pony Friendship is Magic Wiki.html'
    string_start_buffer = """<html>    
    <head>
        <style>
            div {
                width: 60%;
            }
        </style>
    </head>
    
    <body>
        <h1> My Little Pony Script Search Engine </h1>
    """
    for document in document_list['result']:
        title = document["title"]
        document_summary = put_highlight(document["summary"], document_list['query'])
        document_link = web_page_link + '#' + document["link"]
        string_start_buffer +=  '\t<div>\n\t\t\t<a href="'+ document_link +'"><h3>' + title + '</h3></a>' + document_summary + '\t\t\t<br>\n'
        if(len(terms_present(document_list['query'], document['summary'])) > 0):
            string_start_buffer += '\t\t\t<i> Not Included: '
            for terms in terms_present(document_list['query'], document['summary']):
                string_start_buffer += '<del>' +terms + '</del>,'
            string_start_buffer += '</i>\n\t\t</div>\n\t'
        else:
            string_start_buffer += '\t\t</div>\n\t'
    string_end_buffer = string_start_buffer + "</body>\n</html>"
    file.write(string_end_buffer)
    file.close()


if __name__ == "__main__":
    file_writer = open('result.html', 'w')
    mock_data = open('result.json', 'r')
    mock_data = j.load(mock_data)
    write_html(file_writer, mock_data)
