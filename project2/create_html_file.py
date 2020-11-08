import json as j

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

    string_start_buffer = """<html>    
    <head>
        <h2> Result </h2>
    </head>

    <body>
    <p>
    """
    for document in document_list:
        title = document["title"]
        document_summary = document["summary"]
        document_link = document["link"]
        string_start_buffer +=  '\t<b>' + title + '</b> : ' + \
                                '<a href="' + document_link + '"> Document Web Page' + '</a><br>\n' + \
                                '\t\t\t' + document_summary + '</p>\n\t'
    string_end_buffer = string_start_buffer + "</html>"
    file.write(string_end_buffer)
    file_writer.close()


if __name__ == "__main__":
    file_writer = open('project2/result.html', 'w');
    mock_data = open('project2/mock_data.json', 'r')
    mock_data = j.load(mock_data);
    write_html(file_writer, mock_data)
