from bs4 import BeautifulSoup


f = open('p2-data/All Transcripts - My Little Pony Friendship is Magic Wiki.html')

soup = BeautifulSoup(f.read(), 'html.parser')

table_a_tags = soup.findAll(id='mw-content-text')

for a in table_a_tags:
    print(a.prettify())

