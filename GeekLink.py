from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

pageSoup = BeautifulSoup( urlopen('file:///home/vaio/DevCode/Scraping/sitemap.html') , 'html.parser')
links = pageSoup.find_all('a', href = re.compile(r'http://www\.geeksforgeeks\.org.*'))

geekLink = open('geekLink.txt','w')

linkList = list(set([ link['href'] for link in links if link.get('href') != None ]))

for link in sorted(linkList):
	print(link,file = geekLink)

geekLink.close()