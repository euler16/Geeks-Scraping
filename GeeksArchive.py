from bs4 import BeautifulSoup
from urllib.request import urlopen
import pdfkit
import time
import os
import re


visitedLinks = []
abortList = []
count = 0

def PDFdownload( url , filename ,recurDepth = 0, abort = [] ):

	'''This function downloads a given page( URL ) into pdf format in a filenamed
	   given by filename. Uses pdfkit. Aim to handle exceptions.'''

	global count
	try:
		pdfkit.from_url(url,filename)
		count = count + 1
	except OSError:

		if recurDepth < 5:
			print('Waiting ...Resolving RemoveHostClosedError')
			time.sleep(5)
			PDFdownload( url , filename, recurDepth + 1)
		else:
			print('Aborting download of this file:')
			abortList.append( { 'url':url, 'filename':filename } )
			#print(url,' ',filename, file = abortFile)

def nonOrgPageScrap(mainURL,directory = ''):

	'''This Function downloads content from all pages which are in Listed form such as 
	   the archive pages , tag pages , category pages'''


	pageSoup = BeautifulSoup( urlopen(mainURL) , 'html.parser')
	
	if directory != '':
		mainDir = directory + '/' + pageSoup.title.string
	else:
		mainDir = pageSoup.title.string

	if not os.path.exists( mainDir ):
		os.makedirs( mainDir ) 

	#CALCULATES THE NUMBER OF LINKED PAGES
	#CALCULATE LINKED PAGES BY PARSING <nav>
	linkedPages = 0
	navBelowTag = pageSoup.find('nav', id = "nav-below")
	spanTag = navBelowTag.find('span', class_ = 'pages')
	match = re.search(r'Page (\d) of (\d)',str(spanTag.string.rstrip()))

	try:
		linkedPages = int(match.group(2))
	except:
		print('Some Problem in finding Linked pages in listedPage()')


	for i in range(1,linkedPages+1):
		#TRAVERSING ONE LINKED PAGE AFTER ANOTHER
		if mainURL.endswith('/'):
			linkURL = mainURL + 'page/' + str(i) + '/'
		else:
			linkURL = mainURL + '/page/' + str(i) + '/'

		assert linkURL.startswith('http:'), 'problem in linkURL'
		
		linkSoup = BeautifulSoup( urlopen( linkURL ), 'html.parser')
		articleHeaders = linkSoup.find_all('h2', class_ = "entry-title")

		for article in articleHeaders:
			articleLink = article.find('a', href = re.compile(r'http://www\.geeksforgeeks\.org.*'))
			
			if articleLink['href'] not in visitedLinks:
				visitedLinks.append( articleLink['href'] )
				print('Getting '+articleLink.string)
				PDFdownload( articleLink['href'] , mainDir + '/' + articleLink.string+'.pdf', abort = abortList )

			else:
				print(articleLink.string + ' ... Page already visited!!')
			


def orgPageScrap(mainURL,Directory = ''):

	'''This function downloads content from all organised pages ( though they are few ) like Algo, 
	   Note - Doesn't download Java and Python pages ... their structure has small difference that
	   breaks the code... handling that will increase code . It would be better to handle them individually.
	   But it seems there is no need as their content is included in nonOrgPages.'''

	pageSoup = BeautifulSoup( urlopen(mainURL) , 'html.parser')
	directory = Directory + '/' + pageSoup.title.string

	def selectTag(tag):


		''' Geeks for Geeks links are enclosed in the following format:
			<p style = "text-align: center;"> .... </p>
			(<p><em<strong> .... </strong></em></p> OR <p><strong><em>...</em></strong></p>) # Bracket means optional
			<ul>
				<li><a ....> .... </a></li>
				.
				.
				.

			</ul> '''

		boolVal = False

		if tag.name == 'p':
			if tag.get('style') == "text-align: center;":
				boolVal = True

			elif 'em' in [child.name for child in tag.contents]:
				if 'strong' in [subchild.name for subchild in tag.em.contents]:
					boolVal = True

			elif 'strong' in [child.name for child in tag.contents]:
				if 'em' in [subchild.name for subchild in tag.strong.contents]:
					boolVal = True

		elif tag.name == 'ul':
			boolVal = True

		return boolVal

	tag = pageSoup.find('p',style = "text-align: center;")
	
	assert tag.a['name'] != None , 'tag.strong.string is NoneType'

	subDir = '' #directory + '/' + tag.a['name']
	subsubDir = ''# subDir + '/' + ''
	tagList = tag.find_next_siblings(selectTag)

	tagList.insert( 0 , tag )

	assert len(tagList) > 0 , 'tagList is empty in orgPageScrap()'

	for tag in tagList:

		if tag.name == 'p':

			if tag.get('style') == "text-align: center;":
				subDir = directory + '/' + tag.a['name']
				#print('SubDir : ',subDir)
				subsubDir = subDir + '/' + ''
				#print('subsubDir: ',subsubDir)
				if not os.path.exists( subDir ):
					os.makedirs( subDir )

			else:
				assert tag.em.string != None or tag.strong.string, 'tag.em.string is NoneType'
				tagNameAppend = tag.em.string if tag.em.string else tag.strong.string
				subsubDir = subDir + '/' + tagNameAppend
				#print('subsubDir: ',subsubDir)
				if not os.path.exists( subsubDir ):
					os.makedirs( subsubDir )
		elif tag.name == 'ul':
			for liTag in tag.find_all('li'):
				articleURL = liTag.a['href']

				if articleURL not in visitedLinks:
					visitedLinks.append( articleURL )
					print('Downloading ..'+ liTag.a.string )
					PDFdownload( articleURL , subsubDir + '/' + liTag.a.string + '.pdf', abort = abortList )

				else:
					print(liTag.a.string + '... Already visited!!!')
def main():

	ParentDir = 'GeeksForGeeks'
	mainURL = 'http://www.geeksforgeeks.org/'
	
	mainSoup = BeautifulSoup( urlopen(mainURL) , 'html.parser')


	#LINKS TO ALL ORGANIZED PAGES
	orgLinks = ['http://www.geeksforgeeks.org/fundamentals-of-algorithms/',
				'http://www.geeksforgeeks.org/data-structures/',
				'http://www.geeksforgeeks.org/c/',
				'http://www.geeksforgeeks.org/c-plus-plus/',
				]
	#LINKS TO ALL NON-ORGANIZED PAGES
	nonOrgLinks = [
				   'http://www.geeksforgeeks.org/category/c-arrays/',
				   'http://www.geeksforgeeks.org/category/c-strings/',
				   'http://www.geeksforgeeks.org/category/matrix/',
				   'http://www.geeksforgeeks.org/category/linked-list/',
				   'http://www.geeksforgeeks.org/category/stack/',
				   'www.geeksforgeeks.org/category/queue/',
				   'http://www.geeksforgeeks.org/category/hash/',
				   'http://www.geeksforgeeks.org/category/heap/',
				   'http://www.geeksforgeeks.org/category/tree/',
				   'http://www.geeksforgeeks.org/category/binary-search-tree/',
				   'http://www.geeksforgeeks.org/category/graph/',
				   'http://www.geeksforgeeks.org/category/c-puzzles/',
				   'http://www.geeksforgeeks.org/category/bit-magic/',
				   'http://www.geeksforgeeks.org/category/multiple-choice-question/',
				   'http://www.geeksforgeeks.org/category/c-programs/',
				   'http://www.geeksforgeeks.org/category/program-output/',
				   'http://www.geeksforgeeks.org/category/gfact/',
				   'http://www.geeksforgeeks.org/category/guestblogs/']

	for link in nonOrgLinks:
		nonOrgPageScrap( link , ParentDir )

	for link in orgLinks:
		orgPageScrap( link , ParentDir )

	print('Files Downloaded = ', count)

	json.dump(abortList ,  open( 'abortFile.json','w'))


if __name__ == '__main__':
	main()