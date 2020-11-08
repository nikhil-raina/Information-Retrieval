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
    web_page_link = 'p2-data/All Transcripts - My Little Pony Friendship is Magic Wiki.html'
    string_start_buffer = """<html>    
    <head>
        <h2> Result </h2>
    </head>

    <body>
    <p>
    """
    for document in document_list['result']:
        title = document["title"]
        document_summary = put_highlight(document["summary"], document_list['query'])
        document_link = web_page_link + '#' + document["link"]
        string_start_buffer +=  '\t<b>' + title + '</b> : ' + \
                                '<a href="' + document_link + '"><b>' + document["link"] + '</b></a><br>\n' + \
                                '\t\t\t' + document_summary + '</p>\n\t'
    string_end_buffer = string_start_buffer + "</html>"
    file.write(string_end_buffer)
    file_writer.close()


if __name__ == "__main__":
    file_writer = open('result.html', 'w');
    mock_data = open('result.json', 'r')
    mock_data = j.load(mock_data);
    write_html(file_writer, mock_data)
