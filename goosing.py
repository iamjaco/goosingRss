# use goose 3 to get document details
# use Justtext to get full text from html which is provided by goose
# sumy to summarise the text


from goose3 import Goose
import justext
import feedparser
import sumy
import os

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer

LANGUAGE = "english"
SENTENCES_COUNT = 10

class Settings:
    
    FeedList = "feed.txt"
    FeedUrl = "https://feeds.pinboard.in/rss/popular"               # RSS feed to read and post tweets from.
    PostedUrlsOutputFile = "posted-urls.log"           # Log file to save all tweeted RSS links (one URL per line).           
    Blacklisted = ["twitter.com", "dreamwidth.org", "archiveofourown.org", "instagram.com"]
    Language = "english"
    Sentences_count = 10

    
# the different RSS Streams as contained in text file    
# add ios ability to add a new website as rss feed
def getFeed():
    feed = []
    
    with open(Settings.FeedList) as fp: 
        Lines = fp.readlines() 
    for item in Lines: 
        feed.append(item) 
    return feed    


# The function that gets the 
def sum(t):
    document1 = t
    text = ''
    parser = PlaintextParser.from_string(document1,Tokenizer("english"))
    # Using LexRank
    summarizer = LexRankSummarizer()
    #Summarize the document with 2 sentences
    summary = summarizer(parser.document, SENTENCES_COUNT)
    for sentence in summary:
        #text = text + sentence.text
        text = text + str(sentence) +  ' ' 
    return text

def getContent(url):

    g = Goose()
    content = {'Title':'No Content', 'Description':'No Content', 'Canonical' :'No Content', 'Favicon' : 'No Content',
               'Image' : 'No Content', 'Language': 'Unknown', 'Published': 'Unknown','Full_text': 'No content', 'Summary': 'No Content'}
    
    try:
        article = g.extract(url=url)

        if article.title:
            content['Title'] = article.title
        else:
            content['Title'] = article.opengraph.get('title','No Content')

        if article.meta_description:
            content['Description'] = article.meta_description
        else:
            content['Description'] = article.opengraph.get('description','No Content')

        if article.canonical_link:
            content['Canonical'] = article.canonical_link
        else:    
            content['Canonical'] = article.opengraph.get('url','No Content')

        if article.meta_favicon:
            content['Favicon'] = article.meta_favicon

        if article.top_image:
            content['Image'] = article.top_image
        else:
            content['Image'] = article.opengraph.get('image','No Content')

        if article.meta_lang:
            content['Language'] = article.meta_lang

        if article.publish_datetime_utc:
            content['Published'] = article.publish_datetime_utc

        if article.cleaned_text:
            content['Full_text'] = article.cleaned_text

        if content['Full_text'] != 'No Content':
            content['Summary'] = sum(content['Full_text'])
        elif content['Description'] != 'No Content':
            content['Summary'] = content['Description']
        else:
            content['Summary'] = 'No Content'                             
    except:
        pass
        
    return content


def is_in_linkLog(content, filename):
    #Does the content exist in the log file?
    
    # TO DO -> Convert this TO READ FROM to mysql
    if os.path.isfile(filename):
        with open(filename) as f:
            lines = f.readlines()
        if (content + "\n" or content) in lines:
            return True
    
    return False

def is_in_blacklist(content):
    
    # check if link is blacklisted
    for item in Settings.Blacklisted:
        if item.upper() in content.upper():

            return True
    
    return False


def does_have_content(content):
    link, title, description, image, summary = content
    if 'No Content' in content:
        return False
    
    return True

    
def is_content_rubbish():
    pass

def get_summary_of_content():
    pass

def write_to_linkLog(content, filename):
    # Append content to log file
    
    # TO DO -> Convert this to post to mysql
    try:
        with open(filename, "a") as f:
            f.write(content + "\n")
    except IOError as e:
            print(e)


def read_rss(url):
    print("Starting with - " + url)
    feed = feedparser.parse(url)
    if feed:
        for item in feed["items"]:
            link = item.get('link','No content')
           
            #check if link was already posted
            if is_in_linkLog(link, Settings.PostedUrlsOutputFile):
                #print("Already posted:", link)
                pass
            
            else:
                if is_in_blacklist(link):
                    pass
                else:
                    detail =  getContent(link)  
                    if does_have_content((detail["Canonical"], detail["Title"], detail["Description"], detail["Image"], detail["Summary"])): 
                        write_to_linkLog(link, Settings.PostedUrlsOutputFile)
                        print(detail["Title"])
                        print(detail["Summary"])
                        print('---------------')
                        print()
                    else:
                        print('Link unusable due to miussing content')

        
    else:
        print("Nothing found in feed", url) 
    print('Done')    

    
    
for i in getFeed():
        read_rss(url=i)
