from bs4 import BeautifulSoup

def loadFile():
    documents = {} #key=doc; value=document
    transcriptFile = open('project2/p2-data/All Transcripts - My Little Pony Friendship is Magic Wiki.html')
    soup = BeautifulSoup(transcriptFile.read(), 'html.parser')
    transcriptFile.close()
    tags = soup.find(id='mw-content-text').find('p').contents
    currDoc = None
    i=0
    while i < len(tags):
        if tags[i] != '\n':
            if tags[i].name == 'h2':
                currDoc = tags[i].text
                documents[currDoc] = []
            elif currDoc != None:
                if tags[i].name == 'table':
                    attr =  tags[i].attrs
                    if 'class' in  attr.keys() and attr['class'] == 'navbox':
                        break
                    
                documents[currDoc].append(tags[i].text)
        i += 1
    return documents