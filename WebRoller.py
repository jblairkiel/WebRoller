from html.parser import HTMLParser  
from urllib.request import urlopen  
from urllib import parse
from urllib.parse import urlparse
from scanner import *
import sys
import time

def main(argv):
    #URL, Mode, page limit
    
    if(sys.argv[1] == '-h' or sys.argv[1] == "--help"):
        printHelpMessage()
    else:
        #print(sys.argv[1])
        #print(sys.argv[2])
        #domain = stripURL(sys.argv[1])
        spider(sys.argv[1],sys.argv[2])

    #run program with " python3 WebRoller.py http://www.safehomealabama.gov/SHAHome.aspx Alabama "

def stripURL(fullURL):
    #print(fullURL," before")
    parsed_uri = urlparse(fullURL)
    #domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    domain = '{uri.netloc}'.format(uri=parsed_uri) 
    #print(domain," after")
    return domain;
     

# We are going to create a class called LinkParser that inherits some
# methods from HTMLParser which is why it is passed into the definition
class LinkParser(HTMLParser):

    # This is a function that HTMLParser normally has
    # but we are adding some functionality to it
    def handle_starttag(self, tag, attrs):
        exemptLinks = ["tel:","mailto:","javascript:","#","#top"]
        extensions = [".pdf",".pptx",".xlsx",".xls",".doc",".docx"]
        # We are looking for the begining of a link. Links normally look
        # like <a href="www.someurl.com"></a>
        if tag == 'a':
            for (key, value) in attrs:  
                if key == 'href':
                    #print("self.baseURL: ", self.baseUrl, "in: ",value)
                    if (self.domain in value) and not any(exempt in value for exempt in exemptLinks):
                        if("." not in value):
                            #print("Made it here")
                            self.internalLinks = self.internalLinks + [newUrl]
                        #if("revenue.alabama" in value) and not any(exempt in value for exempt in exemptLinks):
                        elif any(e in value for e in extensions):
                            self.documentLinks = self.documentLinks + [value]
                            if not any(e in value for e in self.uniqueDocumentLinks):
                                self.uniqueDocumentLinks = self.uniqueDocumentLinks + [value]
                        elif ("safehomealabama" not in value ):
                        #elif("." and "whitehouse" not in value):
                            self.trueexternalLinks = self.trueexternalLinks + [value]
                        else:
                            # We are grabbing the new URL. We are also adding the
                            # base URL to it. For example:
                            # www.netinstructions.com is the base and
                            # somepage.html is the new URL (a relative URL)
                            #
                            # We combine a relative URL with the base URL to create
                            # an absolute URL like:
                            # www.netinstructions.com/somepage.html
                            newUrl = parse.urljoin(self.baseUrl, value)
                            # And add it to our colection of internalLinks:
                            self.internalLinks = self.internalLinks + [newUrl]

                    elif any (exempt in value for exempt in exemptLinks): 
                        #do nothing
                        continue
                    else:
                        self.externalLinks = self.externalLinks + [value]

    
    # This is a new function that we are creating to get internalLinks
    # that our spider() function will call
    def getLinks(self, url, domain):
        self.internalLinks = []
        self.externalLinks = []
        self.trueexternalLinks = []
        self.documentLinks = []
        self.uniqueDocumentLinks = []
        ignoreHeaders = ["application/pdf"]
        # Remember the base URL which will be important when creating
        # absolute URLs
        self.baseUrl = url
        self.domain = domain
        # Use the urlopen function from the standard Python 3 library
        #print("Made it here")
        response = urlopen(url)
        # Make sure that we are looking at HTML and not other things that
        # are floating around on the internet (such as
        # JavaScript files, CSS, or .PDFs for example)
        #print(response.getheader('Content-Type'))
        if response.getheader('Content-Type')=='text/html; charset=utf-8':
            htmlBytes = response.read()
            #print(htmlBytes)
            # Note that feed() handles Strings well, but not bytes
            # (A change from Python 2.x to Python 3.x)
            htmlString = htmlBytes.decode("utf-8")
            #print("htmlString is: ",htmlString)
            self.feed(htmlString)
            return htmlString, self.internalLinks, self.externalLinks, self.documentLinks, self.uniqueDocumentLinks, self.trueexternalLinks 
        elif response.getheader('Content-Type')=="text/html; charset=utf-8":
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("UTF-8")
            self.feed(htmlString)
            return htmlString, self.internalLinks, self.externalLinks, self.documentLinks, self.uniqueDocumentLinks, self.trueexternalLinks
        elif response.getheader('Content-Type')=="text/html;charset=UTF-8":
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("UTF-8")
            self.feed(htmlString)
            return htmlString, self.internalLinks, self.externalLinks, self.documentLinks, self.uniqueDocumentLinks, self.trueexternalLinks
        elif response.getheader('Content-Type')=="text/html; charset=UTF-8":
            htmlBytes = response.read()
            htmlString = htmlBytes.decode("UTF-8")
            self.feed(htmlString)
        elif response.getheader('Content-Type') in ignoreHeaders:
            return "",[], [], [], [], []
        else:
            print(response.getheader('Content-Type'))
            return "",[], [], [], [], []
    
# And finally here is our spider. It takes in an URL, a word to find,
# and the number of pages to search through before giving up
#URL, Mode, page limit
def spider(url, mode):  
   #Web stats for internal, external
    if(mode == '1'):
        pagesToVisit = [url]
        domain = stripURL(url)
        numberVisited = 0
        foundWord = False
        visitedLinks = []
        visitedExternal = []
        internalLinks = []
        externalLinks = []
        documentLinks = []
        uniqueDocumentLinks = []
        trueexternalLinks = []
        iLinks = 0
        eLinks = 0
        dLinks = 0
        # The main loop. Create a LinkParser and get all the internalLinks on the page.
        # Also search the page for the word or string
        # In our getLinks function we return the web page
        # (this is useful for searching for the word)
        # and we return a set of internalLinks from that web page
        # (this is useful for where to go next)
        #while numberVisited < maxPages and pagesToVisit != []:
        while pagesToVisit != []:
            # Start from the beginning of our collection of pages to visit:
            url = pagesToVisit[0]
            pagesToVisit = pagesToVisit[1:]
            if url not in visitedLinks:
                try:
                    numberVisited = numberVisited +1
                    #print(numberVisited, "Visiting:", url)
                    parser = LinkParser()

                    data, tempI, tempE, tempD, tempTD, tempTE = parser.getLinks(url,domain)
                    externalLinks = externalLinks + tempE
                    internalLinks = internalLinks + tempI
                    documentLinks = documentLinks + tempD
                    uniqueDocumentLinks = uniqueDocumentLinks + tempTD
                    visitedLinks = visitedLinks + [url]
                    trueexternalLinks = trueexternalLinks + tempTE
                    # Add the pages that we visited to the end of our collection
                    # of pages to visit:
                    pagesToVisit = pagesToVisit + tempI 
                    #print(" **Success!**")
                    iLinks = iLinks + 1
                except:
                    print(" **Failed!**\n On page", url)
                    #print("Internal Links:", internalLinks)
            print('Internal',1,'-',len(pagesToVisit))
        print("The num of internallinks:", iLinks)
        print("The num of externallinks:", len(externalLinks))
        print("The num of visited Links are:",len(visitedLinks))
        print("The total count of document links are:", len(documentLinks))
        print("The unique count of document links are:", len(uniqueDocumentLinks))
        print("The true count of external links are:", len(trueexternalLinks))
        printListOnPage(trueexternalLinks)
        writeListToFile(externalLinks,"externalLinks.csv")
        writeListToFile(documentLinks,"documentLinks.csv")
        writeListToFile(visitedLinks,"internalLinks.csv")
    elif(mode == '2'):
        fp = open("siteMap.csv","w")
        domain = stripURL(url)
        pagesToVisit = [url]
        numberVisited = 0
        visitedLinks = []
        visitedExternal = []
        internalLinks = []
        externalLinks = [] 
        documentLinks = []
        iLinks = 0
        eLinks = 0
        dLinks = 0
        tempTD = 0
        #Main Loop
        while pagesToVisit != []:
            url = pagesToVisit[0]
            pagesToVisit = pagesToVisit[1:]
            if url not in visitedLinks:
                try:
                    numberVisited = numberVisited + 1
                    parser = LinkParser()
                    #print("Made it here")
                    data, tempI, tempE, tempD = parser.getLinks(url,domain)
                    #print("Found internal links",tempI)
                    #print("Page:",url)
                    #print("\t[Internal Links]")
                    fp.write("Page:"+url+"\n")
                    fp.write(",[Internal Links]\n")
                    for page in tempI:
                        fp.write(',' + page + "\n")
                    #printListOnPage(tempI)
                    #print("\t[External Links]")
                    #printListOnPage(tempE)
                    #print("\t[Document Links]")
                    #printListOnPage(tempD)
                    visitedLinks = visitedLinks + [url] 
                    # Add the pages that we visted to the end of our collection of pages to visit
                    pagesToVisit = pagesToVisit + tempI
                    iLinks = iLinks + 1
                except:
                    #print(" **Failed!**\n On page",url) 
                    continue
        fp.close()

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor

def printHelpMessage():

    print("  -------------------------------- ")
    print(" /                                \ ")
    print("|          Web Roller v1.0         |")
    print(" \         By: Blair Kiel         /")
    print("  --------------------------------")
    print("")
    print("")
    print("Run program with 'python3 WebRoller.py [URL] [Mode]'")
    print("")
    print("Example: 'python3 WebRoller.py http://www.safehomealabama.gov/SHAHome.aspx Alabama 1'")
    print("")
    print("")
    print("--URL--")
    print("There are many inconsistencies between various URL's.  In order to work correctly,")
    print("    you may have to try entering various forms of a URL.")
    print("")
    print("Ex: https://www.safehomealabama.gov/SHAHome.aspx")
    print("    https://www.safehomealabama.gov/")
    print("    http://www.safehomealabama.gov/SHAHome.aspx")
    print("    http://www.safehomealabama.gov/")
    print("    www.safehomealbama.gov/SHAHome.aspx")
    print("")
    print("--Mode--")
    print("Currently there are two modes supported")
    print()
    print("    1 - (Link Counter)")
    print("    2 - (Site Mapper)")

def printListOnPage(inputList):
    iList = inputList
    for item in iList:
        print('\t',item)

def writeListToFile(inputList,outputName):
    iList = inputList
    fp = open(outputName,"w")
    for item in iList:
        fp.write(item + ";\n")
    fp.close()
     


if __name__ == "__main__":
	main(sys.argv)
