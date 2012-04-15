# Have all homepages in, and a couple of additional pages (from one of the homepages) 
# todo:  
#        figure out how to write the resulting html file to a separate file and then display it
#        add linked pages to the cache
#        think about what I really want the search to do.  Right now it is an OR search, is that really what I want?



#-------------------------------------------------------------------
# create_custom_gallery: creates a custom gallery page for the
# given the search criteria.
#    input: url address of seed page,
#           list of search strings
#    output: an html page with links that satisfy search string
# New procedure
#-------------------------------------------------------------------
def create_custom_gallery(seed, search_list):
    augmented_search_list = augment_search(search_list)
  
    search_string = ''
    for string in search_list:
        search_string = search_string + ' ' + string
        
    header_filename = 'CS101_Contest_headerinfo.txt'
    header_info = load_from_file(header_filename) + search_string + """</samp></h3>"""
    footer_info = """</div><!-- end content --></div><!-- end page --></body></html>"""
    
    index, m_dict = crawl_member_gallery(seed)
    list_urls = lookup(index,augmented_search_list)
    
    page = header_info
    while list_urls:
        page = page + m_dict[list_urls.pop()]
    page = page + footer_info
    return page

#-------------------------------------------------------------------
# crawl-member-gallery: crawls the websites of all members in the
# gallery, creating an dictionary of keywords to urls, and a
# dictionary of urls to member divs.
#   input: url of member gallery page
#   output: dictionary of search strings to urls                   
#           dictionary of urls to member divs
# New procedure modeled on crawl_web procedure
#-------------------------------------------------------------------
def crawl_member_gallery(seed):
    m_dict = create_member_dictionary(seed)
    tocrawl = m_dict.keys()      #  gets a list of all homepages for members
    crawled = []
    index = {}
    # crawl the homepage of each member
    for homepage in tocrawl:
        tocheck = [homepage]
        while tocheck:
            page = tocheck.pop()
            if page not in crawled:
                 content = get_page(page)
                 if content:
                     add_page_to_index(index, homepage, content)
                     next_to_crawl = get_all_pertinent_links(homepage,content)
                     union(tocheck, next_to_crawl)
                 crawled.append(page)
    return index, m_dict


#-------------------------------------------------------------------
# create_member_dictionary: creates a dictionary of urls to         
# member divs for each member listed on the seed page               
#   input:  url for page to search for information                  
#   output:  dictionary of {url: member div}
# New procedure
#-------------------------------------------------------------------
def create_member_dictionary(seed):
    member_gallery = get_page(seed)    # get the page to process
   
    member_dict = {}
    
    while True:
        next_member_start = member_gallery.find("<div class='leftbox3'>")
        if next_member_start == -1:
            return member_dict
        next_member_end = member_gallery.find('</div>',next_member_start)
        value = member_gallery[next_member_start:next_member_end+6]
        ahref_start = value.find('<a href=')
        if ahref_start == -1:
             print 'Something bad, a href tag should be there'
        start_quote = value.find('"', ahref_start)
        if start_quote == -1 or start_quote > next_member_end:
            start_quote = value.find("'", ahref_start)
            end_quote = value.find("'",start_quote + 1)
        else:
            end_quote = value.find('"', start_quote + 1)
        url = value[start_quote + 1: end_quote]
        
        if url:
            member_dict[url[7:]] = value   # don't remember "http://" part
        member_gallery = member_gallery[next_member_end:]


#-------------------------------------------------------------------#
# augment_search: takes a search list and augments it, based on    
# search items.  Add different forms of the following fiber-related
# words: knit, dye, bead, crochet, weave, felt,
#    input: list of search keywords                                        
#    output: augmented list of search keywords
# New procedure
#-------------------------------------------------------------------#
def augment_search(s_list):
    fiber_list = [['weave','weaves', 'weaving', 'weaver', 'wove'],
                  ['knit','knits', 'knitting', 'knitter', 'knitted'],
                  ['dye','dyes', 'dyeing', 'dyer', 'dyed'],
                  ['bead','beads', 'beading', 'beader', 'beaded'],
                  ['crochet','crochets', 'crocheting', 'crocheter', 'crocheted'],
                  ['quilt','quilts', 'quilting', 'quilter', 'quilted'],
                  ['spin', 'spins', 'spinning', 'spinner', 'spun'],
                  ['felt', 'felts', 'felting', 'felter', 'felted'],
                  ['basket', 'baskets', 'basketmaking', 'basketmaker'],
                  ['paper', 'papers', 'papermaking', 'papermaker'] ]
    new_list = []
         
    for word in s_list:    # for each keyword in our search list
        notfound = True
        for f_word in fiber_list:   # for each set of fiber words we care about
            if word in f_word:         #  the search keyword is one we care about
                union(new_list,f_word)   #  add the list associated with that word
                notfound = False         
                break
        if notfound:             # if keyword isn't one we care about
            new_list.append(word)     #  put it on the list now
   
    return new_list


#-------------------------------------------------------------------
# get_all_pertinent_links: gets all the links on the input page
# that are within the same domain name of the input page
#   input: url of homepage
#   output: list of all urls within the same domain linked to
#           by the homepage
# New procedure, modeled on existing procedure get_all_links
#-------------------------------------------------------------------#
def get_all_pertinent_links(homepage,page):
    links = []
    while page:
        url, endpos = get_next_target(page)
        if url:
            # if url is a complete address and contains our homepage, use it
            if homepage in url:
                links.append(url)
            else:
                # if url is incomplete, complete and use it
                if 'http:' not in url:
                    links.append(homepage + '/' + url)
        #  Get to the next else for three reasons:
        #  1)get-next_target returned None for url because no more <a ...>
        #  tags, then end_pos == -1, done, get out
        #  2) get_next_target returned None, it found <a ...> tag,
        #  but not href attribute, endpos != -1, keep searching
        #  3) get_next_target returned an empty list because <a ...> tag
        #  was found, it had an href attribute, but the value of that
        #  attribute was empty, endpos != -1, keep searching
        else:  #  there was no url or there was no more <a
            if endpos == -1:   #  have looked at everything on this page, 
                break          #  we are done, get out
        page = page[endpos:]
    return links


#-------------------------------------------------------------------#
# get_next_target: look for the next target url
#   input: string representation of the page
#   output: the next url found
#           the next position in the page to look for next target
# Modifications: this routine has been changed to find a href attribute that
# doesn't immediately following the "<a " of an a tag; to allow
# for the use of single or double quotes in the href attribute;
# and to act gracefully when an empty href attribute is found
# (i.e. "href=''")
#-------------------------------------------------------------------#
def get_next_target(page):
    # find an "<a...> html tag
    start_a = page.find('<a ')
    end_a = page.find('>', start_a)
    if end_a == -1 or start_a == -1:     #  no more <a ...> tags, we are done
        return None, -1

    # we have an <a ...> tag, look for an href attribute
    start_link = page.find('href=', start_a)
    if (start_link == -1 or start_link > end_a):   # if no href attribute
        return None, end_a                         # return pos end <a ..> tag
    
    # we have a href attribute, look for a single or double quote
    start_quote = page.find('"', start_link)
    if start_quote == -1 or start_quote > end_a:   # no double quote, look for single
        start_quote = page.find("'", start_link)
        end_quote = page.find("'", start_quote + 1)
    else:
        end_quote = page.find('"', start_quote + 1)

    url = page[start_quote + 1:end_quote]
    return url, end_quote


#----------------------------------------------------------------------------
#  union: append all the elements in the second list to the first list
#     input: list which will be appended to
#            list which provides elements to append
#     output: None (first list is modified)
# Existing procedure, no changes.
#----------------------------------------------------------------------------   
def union(a, b):
    for e in b:
        if e not in a:
            a.append(e)


#----------------------------------------------------------------------------
#  add_page_to_index: adds all words in the given page to the index
#     input: index of keyword: [url, ...] pairs to modify
#            url of webpage to associated with these keyword occurrences
#            contents of the webpage from which to extract keywords
#     output: None (index is modified)
# Modifications: call the new procedure to split the page contents into a list
# of keywords, based on the list of delimitor characters specified
#----------------------------------------------------------------------------   
def add_page_to_index(index, url, content):    
    if not content:
        return
    content = strip_html_tags(content)
   
    words = split_string(content,[' ', ',', '.', '!', '?', ':', ';', '"',
                                  '/', "'", ')', '(', '{', '}', '[', ']', '\n', '\t',
                                  '|'])
   
    for word in words:
        add_to_index(index, word, url)

        
#----------------------------------------------------
# strip_html_tags: take out all html tags
#   input: string to process
#   output:  string with all html tags removed
# New procedure
#----------------------------------------------------
def strip_html_tags(string):
    # hmm, how to do this without stripping < or > that are not part of tags?
    output = ''
    end_tag = 0
    while True:
        start_tag = string.find('<', end_tag)   # find start of a tag
        if start_tag == -1:        # no more <?  we are done
            return output
        output = output + ' ' + string[end_tag:start_tag]   # add all to this start tag
        # have found start of an html tag, could it be a comment?
        start_html_cmt = string.find('<!--', end_tag)
        if start_html_cmt == start_tag:   #  yes, this is an html comment
            end_tag = string.find('-->',start_tag) + 2    # look for end html cmt
        else:
            end_tag = string.find('>', start_tag)        # find end of the tag
        if end_tag == -1:
            # very curious, had a start tag with no end tag
            return output
        end_tag = end_tag + 1   # step over the ending >
     

#----------------------------------------------------
# split_string: splits a string into a list of words,
# based on a list of delination characters.
#   input: string which needs to be split up;
#          list of word delination characters
#   output: list of words
# This is the routine given by instructors as answer
# to homework 4.5
#----------------------------------------------------
def split_string(source, split_list):
    output = []
    atsplit = True
    for char in source:
        if char in split_list:
            atsplit = True
        else:
            if atsplit:
                output.append(char)
                atsplit = False
            else:
                output[-1] = output[-1] + char  #  add last char to last word
    return output

        
#----------------------------------------------------------------------------
#  add_to_index: adds a keyword: url pair to the index
#     input: a dictionary of the form: {keyword: [url, ...], ...}
#            one keyword
#            url that goes with that keyword
#     output: none, specifically
# Modification:  translate all keywords to lowercase before adding to index
#----------------------------------------------------------------------------                
def add_to_index(index, keyword, url):
    keyword = keyword.lower()
    if keyword in index:
        if url not in index[keyword]:
            index[keyword].append(url)
    else:
        index[keyword] = [url]


#----------------------------------------------------------------------------
#  lookup: looks up a list of words in the index and returns a list of
#  urls that contain any of those words.
#     input: a dictionary of the form: {keyword: [url, ...], ...}
#            a list of keywords
#     output: a list of urls that contain any of the keywords
# Modification: translate all keywords to lowercase;
#               look for multiple keywords, don't have to be consecutive to be a match
#----------------------------------------------------------------------------
def lookup(index, keywords):
    
    current_list = []

    # collect all the urls that go with each keyword
    for kword in keywords:
        kword = kword.lower()
        if kword in index:    
            # append any new urls to current_list
            for url in index[kword]:
                if url not in current_list:
                    current_list.append(url)
                  
    return current_list

    
#----------------------------------------------------------------------------
#  get_page: gets the page contained in the url
#     input: url of webpage to get
#     output: contents of the url
#----------------------------------------------------------------------------   
def get_page(url):
    if url in cache:
        return cache[url]
    else:
        #print "Page not in cache: " + url
        return None

#----------------------------------------------------------------------------
#  load_from_file: loads the contents of a file
#     input: filename of file to load
#     output: contents of the file
# I didn't know how to read and write from file.  I looked at the github
# code for Louie Orbeta's project and learned how to do this.  Thanks Louie.
#----------------------------------------------------------------------------

def load_from_file(filename):
    
    myfile = open(filename,'r')
    mystuff = myfile.read()
    myfile.close()
    return mystuff


#----------------------------------------------------------------------------
# Start of the actual code:
# 1. read in and create the cache file of webpages
# 2. call create_custom_gallery to do all the work -- create a custom
# html page containing only those entries that match the search criteria
# 3. print out that created page.  To see the page, you have to copy it into
#    a file and then display it with a web browser.  I have to figure out how
#    to do that automatically
#----------------------------------------------------------------------------


execfile('CS101_Contest_cache.txt')
 
myurl = 'http://www.handweaversofboulder.org/membergallery.html'
newpage = create_custom_gallery(myurl,['weave', 'the', 'and'])
print newpage



