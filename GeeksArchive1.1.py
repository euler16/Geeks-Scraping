from bs4 import BeautifulSoup
from urllib.request import urlopen
import pdfkit
import time
import os
import re

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

	#def downloadPage( linkSoup ):
	#	#DOWNLOADS A SINGLE PAGE





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
	if spanTag == None:
		#no span tag probably the only page
		linkedPages = 1

	else:	
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
			
	        #if articleLink['href'] not in visitedLinks:

		    #	visitedLinks.append( articleLink['href'] )
		    #	with open( 'visitedLink.txt', 'a' ) as fp:
		    #		print( articleLink['href'] , file = fp )
		  	#visitedFile = open('visitedLinks.json','w')
		 	#json.dump( visitedLinks, visitedFile )
		 	#visitedFile.close()

	 		print('Getting '+articleLink.string)
	 		if os.path.isfile( mainDir + '/' + articleLink.string+'.pdf' ) == True:
	 			print(' File already downloaded...')
	 		else:
	 			PDFdownload( articleLink['href'] , mainDir + '/' + articleLink.string+'.pdf', abort = abortList )

		#else:
		#		print(articleLink.string + ' ... Page already visited!!')
		


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

	tagList.insert( 0 , tag 	)

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

			#	if articleURL not in visitedLinks:
			#		visitedLinks.append( articleURL )

					#visitedFile = open('visitedLinks.json','w')
					#json.dump( visitedLinks, visitedFile )
					#visitedFile.close()
			#		with open( 'visitedLink.txt', 'a' ) as fp:
			#			print( articleURL , file = fp )

				print('Downloading ..'+ liTag.a.string )
				if os.path.isfile( subsubDir + '/' + liTag.a.string + '.pdf' ):
					print(' File already downloaded...')
				else:
					PDFdownload( articleURL , subsubDir + '/' + liTag.a.string + '.pdf', abort = abortList )

			#	else:
			#		print(liTag.a.string + '... Already visited!!!')

def downloadFailedDownloads(failedList,directory):

	if len(failedList) == 0:
		print('All Files downloaded')
		return
	fList = []
	print( '\nTrying to download failed Files Again ...')
	for page in failedList:
		url = page['url']
		filename = directory + '/' + page['filename'].split('/')[-1]
		PDFdownload( url , filename , abort = fList)
		failedList.pop( page )

	return fList

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
				   'http://www.geeksforgeeks.org/category/matrix/'	   
				   'http://www.geeksforgeeks.org/category/linked-list/',
				   'http://www.geeksforgeeks.org/category/stack/',
				   'http://www.geeksforgeeks.org/category/queue/',
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
				   'http://www.geeksforgeeks.org/category/guestblogs/'
				   'http://www.geeksforgeeks.org/category/c-arrays/'	
				   'http://www.geeksforgeeks.org/category/c-strings/'
				   'http://www.geeksforgeeks.org/category/matrix/',	
				   'http://www.geeksforgeeks.org/category/linked-list/',
				   'http://www.geeksforgeeks.org/category/stack/',
				   'http://www.geeksforgeeks.org/category/queue/',
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
				   'http://www.geeksforgeeks.org/category/guestblogs/',
				   'http://www.geeksforgeeks.org/category/advanced-data-structure/',
				   'http://www.geeksforgeeks.org/category/algorithm/analysis/',
				   'http://www.geeksforgeeks.org/category/algorithm/mathematical/',
				   'http://www.geeksforgeeks.org/category/algorithm/pattern-searching/',
				   'http://www.geeksforgeeks.org/category/algorithm/randomized/',
				   'http://www.geeksforgeeks.org/category/algorithm/sorting/',
				   'http://www.geeksforgeeks.org/category/competitive-programming/',
				   'http://www.geeksforgeeks.org/category/design/',
				   'http://www.geeksforgeeks.org/category/interview-experiences/',
				   'http://www.geeksforgeeks.org/category/interview-experiences/experienced-interview-experiences/',
				   'http://www.geeksforgeeks.org/category/interview-experiences/internship-interview-experiences/',
				   'http://www.geeksforgeeks.org/category/java/',
				   'http://www.geeksforgeeks.org/category/pattern-searching/',
				   'http://www.geeksforgeeks.org/category/project/',
				   'http://www.geeksforgeeks.org/category/searching/',
				   'http://www.geeksforgeeks.org/category/sorting/',
				   'http://www.geeksforgeeks.org/tag/Greedy-Algorithm/',
				   'http://www.geeksforgeeks.org/tag/dynamic-programming/',
				   'http://www.geeksforgeeks.org/tag/divide-and-conquer/',
				   'http://www.geeksforgeeks.org/tag/geometric-algorithms/',
				   'http://www.geeksforgeeks.org/tag/recursion/',
				   'http://www.geeksforgeeks.org/tag/gate/	',
				   'http://www.geeksforgeeks.org/tag/gate-cs-ds-algo/',
				   'http://www.geeksforgeeks.org/tag/gate-cs-older/',
				   'http://www.geeksforgeeks.org/tag/advanced-data-structures/',
				   'http://www.geeksforgeeks.org/tag/array/',
				   'http://www.geeksforgeeks.org/tag/stack/',
				   'http://www.geeksforgeeks.org/tag/gfact/',
				   'http://www.geeksforgeeks.org/tag/java/',
				   'http://www.geeksforgeeks.org/tag/graph/',
				   'http://www.geeksforgeeks.org/tag/bit-magic/',
				   'http://www.geeksforgeeks.org/tag/hashing/',
				   'http://www.geeksforgeeks.org/tag/pattern-searching/',
				   'http://www.geeksforgeeks.org/tag/stack-queue/',
				   'http://www.geeksforgeeks.org/tag/c-puzzle/',
				   'http://www.geeksforgeeks.org/tag/operating-systems/',
				   'http://www.geeksforgeeks.org/tag/mathematicalalgo/',
				   'http://www.geeksforgeeks.org/tag/python/',
				   'http://www.geeksforgeeks.org/tag/c/',
				   'http://www.geeksforgeeks.org/tag/backtracking/',
				   'http://www.geeksforgeeks.org/tag/puzzle/',
				   'http://www.geeksforgeeks.org/tag/morgan-stanley/',
				   'http://www.geeksforgeeks.org/tag/flipkart/',
				   'http://www.geeksforgeeks.org/tag/goldman-sachs/',
				   'http://www.geeksforgeeks.org/tag/dbms/',
				   'http://www.geeksforgeeks.org/tag/sap-labs/',
				   'http://www.geeksforgeeks.org/tag/oracle/',
				   'http://www.geeksforgeeks.org/tag/stl/',
				   'http://www.geeksforgeeks.org/tag/microsoft/',
				   'http://www.geeksforgeeks.org/tag/amazon/',
				   'http://www.geeksforgeeks.org/tag/maq-software/',
				   'http://www.geeksforgeeks.org/tag/matrix/',
				   'http://www.geeksforgeeks.org/tag/snapdeal/',
				   'http://www.geeksforgeeks.org/tag/d-e-shaw/',
				   'http://www.geeksforgeeks.org/tag/design/',
				   'http://www.geeksforgeeks.org/tag/interview-experience/',
				   'http://www.geeksforgeeks.org/tag/zoho/',
				   'http://www.geeksforgeeks.org/tag/cn/',
				   'http://www.geeksforgeeks.org/tag/samsung/',
				   'http://www.geeksforgeeks.org/tag/google/',
				   'http://www.geeksforgeeks.org/tag/adobe/'
]

	for link in nonOrgLinks:
		nonOrgPageScrap( link , ParentDir )

	for link in orgLinks:
		orgPageScrap( link , ParentDir )

	print('Files Downloaded = ', count)

	#json.dump(abortList ,  open( 'abortFile.json','w') )
	failedList = downloadFailedDownloads( abortList , ParentDir )
	failedList = failedList[:]
	failedFile = open('failedLinks.txt','w')
	for link in failedList:
		print( link, failedFile )
		

	#json.dump( failedList , open( 'failedFile.json','w') )
	
	if len( abortList ) != 0:
		print( 'Some errors in abortList and failedList .... check corresponding files')

if __name__ == '__main__':
	main()