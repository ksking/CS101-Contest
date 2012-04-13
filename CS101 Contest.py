# Have two homepages in and can do multiple word searches
# todo:  figure out how to store caches in a separate file and import it
#        figure out how to write the resulting html file to a separate file and then display it
#        add other homepages to the cache
#        add linked pages to the cache
#        get rid of all newline denotations ("\n") do this in split_string


#-------------------------------------------------------------------
# create_custom_gallery: creates a custom gallery page for the
# given the search criteria.
#    input: url address of seed page,
#           list of search strings
#    output: an html page with links that satisfy search string
# New procedure
#-------------------------------------------------------------------
def create_custom_gallery(seed, search_list):
    search_string = ''
    for string in search_list:
        search_string = search_string + ' ' + string
        # is there a reason to have the input to this routine be a list of search arguments instead of a string of such?
        
    header_info = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang='en' xml:lang='en' xmlns='http://www.w3.org/1999/xhtml'>
<head> 
     <title>Handweavers Guild of Boulder: Gallery</title>
     <meta  http-equiv='Content-Type' content='text/html; charset=utf-8'/> 
     <meta name='keywords' content='weaving, Boulder, Handweavers, fiber, guild,member,gallery'/>
     <link href='http://www.handweaversofboulder.org/images/favicon.ico' rel='shortcut icon'/>
     <link rel='stylesheet'  type='text/css' href='http://www.handweaversofboulder.org/defaultcss.css' media='screen' title='HGB Default css'/>
     <script type="text/javascript" src="http://www.handweaversofboulder.org/scripts/jquery-1.4.2.min.js"></script>
     <script type="text/javascript" src="http://www.handweaversofboulder.org/scripts/random_banner.js"></script>
     <!--[if IE]>
          <link  rel='stylesheet' type='text/css' href='http://www.handweaversofboulder.org/stupidIEhack.css' media='screen'/>
     <![endif]-->
</head><body><div id='page'><div id='banner'>Handweavers Guild of Boulder</div><!-- end banner -->
<div id='content'><h3>Members Satisfying Your Search Arguments of:    <samp>""" + search_string + """</samp></h3>""" 
    footer_info = """</div><!-- end content --></div><!-- end page --></body></html>"""
    
    index, m_dict = crawl_member_gallery(seed)
    list_urls = lookup(index,search_list)
    
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
    tocrawl = pull_keys(m_dict)      #  gets a list of all homepages for members
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
# pull_keys: take a dictionary, and create a list of all the keys   
# in that dictionary.                                               
#    input: dictionary                                        
#    output: list of keys from the dictionary
# New procedure
#-------------------------------------------------------------------#
def pull_keys(dict):
    result = []
    for entry in dict:
        result.append(entry)
    return result


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
        endquote_quote = page.find("'", start_quote + 1)
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
                                  '/', "'", ')', '(', '{', '}', '[', ']'])
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
        output = output + ' ' + string[end_tag:start_tag]   # add everything up to this start tag
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
#  urls that contain all those words.
#     input: a dictionary of the form: {keyword: [url, ...], ...}
#            a list of keywords
#     output: a list of urls that contain all the keywords
# Modification: translate all keywords to lowercase;
#               look for multiple keywords, don't have to be consecutive to be a match
#----------------------------------------------------------------------------
def lookup(index, keywords):
    for i in range(0, len(keywords)):   # translate all keywords to lowercase
        keywords[i] = keywords[i].lower()

    if keywords[0] not in index:
        return []
    current_list = index[keywords[0]]       # current_list = current list of urls to consider
    
    for kword in keywords[1:]:
        if kword not in index:
            return []
        next_list = index[kword]
        new_list = []
        for i in range(0, len(current_list)):  # for each url in the list of current possible urls
            if current_list[i] in next_list:       #  if that url is in the list for this next word
                new_list.append(current_list[i])   # append it to the list of urls that are still possible   
        current_list = new_list[:]                        
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
        print "Page not in cache: " + url
        return None

    
#def crawl_web(seed): # returns index, graph of inlinks
#    tocrawl = [seed]
#    crawled = []
#    graph = {}  # <url>, [list of pages it links to]
#    index = {} 
#    while tocrawl: 
#        page = tocrawl.pop()
#        if page not in crawled:
#            content = get_page(page)
#            add_page_to_index(index, page, content)
#            outlinks = get_all_links(content)
#            graph[page] = outlinks
#            union(tocrawl, outlinks)
#            crawled.append(page)
#    return index, graph

#def get_all_links(page):
#    links = []
#    while True:
#        url, endpos = get_next_target(page)
#        if url:
#            links.append(url)
#            page = page[endpos:]
#        else:
#            break
#    return links


cache = {
    
    'http://www.handweaversofboulder.org/membergallery.html':
"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang='en' xml:lang='en' xmlns='http://www.w3.org/1999/xhtml'>
<head> 
     <title>Handweavers Guild of Boulder: Gallery</title>
     <meta  http-equiv='Content-Type' content='text/html; charset=utf-8'/> 
     <meta name='keywords' content='weaving, Boulder, Handweavers, fiber, guild,member,gallery'/>
     <link href='http://www.handweaversofboulder.org/images/favicon.ico' rel='shortcut icon'/>
     <link rel='stylesheet'  type='text/css' href='defaultcss.css' media='screen' title='HGB Default css'/>
     <script type="text/javascript" src="/scripts/jquery-1.4.2.min.js"></script>
     <script type="text/javascript" src="/scripts/random_banner.js"></script>
     <!--[if IE]>
          <link  rel='stylesheet' type='text/css' href='stupidIEhack.css' media='screen'/>
     <![endif]-->
</head>
<body>     
<div id='page'>
<div id='banner'>
Handweavers Guild of Boulder

</div>  <!-- end banner -->


<div id='content'>

<h1>Member Gallery</h1>
<p>Many HGB members are well-known outside of HGB, exhibiting works in national shows,
owning or managing businesses, creating custom items for customers, documenting their
creative processes on their own websites.
Here's a gallery of such members.</p>

<!--template for gallery entries, use one or the other of the height/width specifications,
         depending on whether the image is landscape (use width) or portraite (use height)
<div class='leftbox3'>
<a href='' target='_new'>
<b>Member Name</b></a><br/>craft
<img height='230px' width='230px' alt='image'
              src='http://www.handweaversofboulder.org/memberartists/xxxxx.jpg'/>
</div>
-->

<div class='leftbox3'>
<a href='http://www.theknitter.com' target='_new'>
<b>Judy Alexander</b></a><br/>knitting
<img height='230px' width='230px' alt='image'
              src='http://lib.store.yahoo.net/lib/the-knitter/sc-peacock.jpg'/>
</div>

<div class='leftbox3'>
<a href='http://www.marybalzer.com' target='_new'>
<b>Mary Balzer</b></a><br/>coiling, knitting, crocheting, beading
<img height='210px' alt='image'
              src='http://www.handweaversofboulder.org/memberartists/MaryBalzer.jpg'/>
</div>

<div class='leftbox3'>
<a href='http://www.sapphireskyfiberarts.com' target='_new'>
<b>Deanna Curry-Elrod</b></a><br/>felting
<img width='230px' alt='image' src='http://www.handweaversofboulder.org/memberartists/DeannaCurry-Elrod.jpg'/>
</div>

<div class='leftbox3'>
<a href='http://www.davisrestoration.com' target='_new'>
<b>Debbie Davis</b></a><br/>weaving, textile restoration
<img height='230px' width='230px' alt='image'
              src='http://www.davisrestoration.com/images/teec-davis_002_wjwh.jpg'/>
</div>

<div class='leftbox3'>
<a href="http://www.lafarrelly.blogspot.com" target='_new'>
<b>Linda Farrelly</b></a>
<br/>          
<img height='230px' alt="image" src='http://www.handweaversofboulder.org/memberartists/LindaFarrelly.jpg'/>

          
</div>


<div class='leftbox3'>
<a href='http://www.GardnersDelights.com' target='_new'>
<b>Barb Gardner</b></a><br/>quilting
<img height='230px' alt='image' src='http://www.handweaversofboulder.org/memberartists/BarbGardner.jpg'/>
</div>

<div class='leftbox3'>
<a href='http://www.gfwsheep.com' target='_new'>
<b>Joanna Gleason</b></a><br/>fleeces, roving, wool
<img height='230px' width='230px' alt='image'
              src='http://www.gfwsheep.com/flock/starbuck.jpeg'/>
</div>

<div class='leftbox3'>
<a href='mailto:spinaboutyarn@gmail.com?subject=Handspun Yarn Business, From HGB Website' target='_new'>
<b>Gina Hebert</b></a><br/>handspun yarn
<img height='230px' width='230px' alt='image'
              src=''/>
</div>

<div class='leftbox3'>
<a href='http://www.pkldesigns.com' target='_new'>
<b>Phillipa K. Lack</b></a><br/>silk painter
<img width='230px' alt='image' src='http://www.handweaversofboulder.org/memberartists/PhillipaLack.jpg '/>
</div>

<div class='leftbox3'>
<a href='http://www.maryjolawrence.com' target='_new'>
<b>Mary Jo Lawrence</b></a><br/>quilting
<img width='230px' alt='image' src='http://www.handweaversofboulder.org/memberartists/MaryJoLawrence.jpg '/>
</div>

<div class='leftbox3'>
<a href='http://www.fiberexpression.com' target='_new'>
<b>Maryse Levenson</b></a><br/> weaving<br/>
<img height='230px' alt='image' src='http://www.handweaversofboulder.org/memberartists/MaryseLevenson.jpg'/>
</div> 

<div class='leftbox3'>
<a href='http://www.TheFyberCafe.com' target='_new'>
<b>Pat Martinek</b></a><br/>spinning, felting, fleece preparation
<img width='230px' alt='image' src='http://www.handweaversofboulder.org/memberartists/PatMartinek.jpg'/>
</div>

<div class='leftbox3'>
<a href='http://www.Natura.vpweb.com' target='_new'>
<b>Liz Moncrief</b></a><br/>hand-made soap, weaving
<img height='230px' width='230px' alt='image'
              src='http://natura.vpweb.com/666_500_csupload_5764335.jpg?u=3448183052'/>
</div>
  
<div class='leftbox3'>
<a href='http://www.amymundinger.com' target='_new'>
<b>Amy Mundinger</b></a><br/>fiber art and jewelry design
<img width='230px' alt='image' src='http://www.handweaversofboulder.org/memberartists/AmyMundinger.jpg'/>
</div>

<div class='leftbox3'>
<a href='http://web.mac.com/allgoodwishes/All_Good_Wishes' target='_new'>
<b>Heide Murray</b></a><br/>needle felting<br/>
<img  height='230px' alt='image' src='http://www.handweaversofboulder.org/memberartists/HeideMurray.jpg'/>
</div>

<div class='leftbox3'>
<a href='http://www.deniseperreault.com' target='_new'>
<b>Denise Perreault</b></a><br/>beadwork   
<img width='230px' alt='image' src='http://www.handweaversofboulder.org/memberartists/DenisePerrault.jpg'/>
</div>

<div class='leftbox3'>
<a href='http://www.fiberartbywolfer.com' target='_new'>
<b> Joan Wolfer</b></a><br/>needlework<br/>
<img height='230px' alt='image' src='http://www.handweaversofboulder.org/memberartists/JoanWolfer.jpg'/>
</div>

</div>   <!-- end content -->
</div>   <!-- end page -->
</body></html>""",
   'www.fiberartbywolfer.com':
    """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />


<meta name="KEYWORDS" content="Fiberart, fiber art, Wall Hangings, canvas work, mixed media, Boulder County Arts Association, Joan Wolfer, Fiberart by Wolfer, Fiber Canvaswork, Pole People, fiberart Boulder">

<meta name="google-site-verification" content="-Kiw4xqXCGdW50BxkU9dVbOT-i4pml8RG9XyxHLjGx0" />

<title>Fiberart By Wolfer | Boulder, Colorado | Joan Wolfer | Fiber Canvaswork</title>


<meta name="DESCRIPTION" content="Boulder Colorado artist Joan Wolfer creates Fiberart Wall Hangings Pole People. Member of the Boulder Colorado Arts Association. Embellished mixed media fiberart.">

<meta name="robots" content="index, follow">
<meta http-equiv="Content-Language" content="en">
<meta name="googlebot" content="index, follow">
<meta name="MSSmartTagsPreventParsing" content="true">
<meta name="Rating" content="General">
<meta name="revisit-after" content="5 Days">
<meta name="document-classification" content="internet">
<meta name="document-type" content="Public">
<meta name="document-rating" content="Safe for Kids">
<meta name="document-distribution" content="Global">
<meta name="copyright" content="Copyright &copy; 2010 by Schloss Web Services - Fairfield Web Design." />
<meta name="author" content="Schloss Web Services" />
<meta name="author" content="tracy@schloss.com" />
<meta name="distribution" content="global" />


<link href="include/wolfer.css" rel="stylesheet" type="text/css" />

<script type="text/javascript">
<!--
function MM_preloadImages() { //v3.0
  var d=document; if(d.images){ if(!d.MM_p) d.MM_p=new Array();
    var i,j=d.MM_p.length,a=MM_preloadImages.arguments; for(i=0; i<a.length; i++)
    if (a[i].indexOf("#")!=0){ d.MM_p[j]=new Image; d.MM_p[j++].src=a[i];}}
}
function MM_swapImgRestore() { //v3.0
  var i,x,a=document.MM_sr; for(i=0;a&&i<a.length&&(x=a[i])&&x.oSrc;i++) x.src=x.oSrc;
}

function MM_findObj(n, d) { //v4.01
  var p,i,x;  if(!d) d=document; if((p=n.indexOf("?"))>0&&parent.frames.length) {
    d=parent.frames[n.substring(p+1)].document; n=n.substring(0,p);}
  if(!(x=d[n])&&d.all) x=d.all[n]; for (i=0;!x&&i<d.forms.length;i++) x=d.forms[i][n];
  for(i=0;!x&&d.layers&&i<d.layers.length;i++) x=MM_findObj(n,d.layers[i].document);
  if(!x && d.getElementById) x=d.getElementById(n); return x;
}

function MM_swapImage() { //v3.0
  var i,j=0,x,a=MM_swapImage.arguments; document.MM_sr=new Array; for(i=0;i<(a.length-2);i+=3)
   if ((x=MM_findObj(a[i]))!=null){document.MM_sr[j++]=x; if(!x.oSrc) x.oSrc=x.src; x.src=a[i+2];}
}
//-->
</script>



</head>

<body onload="MM_preloadImages('images/home-off.gif','images/home-on.gif','images/mixed-on.gif','images/fiber-on.gif','images/poleperson-on.gif','images/about-artist-on.gif','images/contact-on.gif','images/canvas-on.gif')">
<div id="layout">

<div id="header"><img src="images/Banner.gif" width="950" height="101" /></div>
  <!-- end header div here-->
  <div id="nav">
  <table width="950" border="0" cellspacing="0" cellpadding="0">
  <tr>
    <td width="155"><a href="index.html"><img src="images/home-on.gif" alt="Joan Wolfer Fiber Art" name="Image1" width="155" height="46" border="0" id="Image1"/></a></td>
    
    <td width="152"><a href="canvaswork1.html"><img src="images/canvas-off.gif" alt="Joan Wolber Canvasworks" name="Image2" width="152" height="46" border="0" id="Image2" onmouseover="MM_swapImage('Image2','','images/canvas-on.gif',1)" onmouseout="MM_swapImgRestore()" /></a></td>
    
    <td width="150"><a href="pole1.html"><img src="images/poleperson-off.gif" alt="Joan Wolfer Poleperson" width="150" height="46" border="0" id="Image3" onmouseover="MM_swapImage('Image3','','images/poleperson-on.gif',1)" onmouseout="MM_swapImgRestore()" /></a></td>
    <td width="150"><a href="mixed.html"><img src="images/mixed-off.gif" alt="Joan Wolfer Mixed Media" width="150" height="46" border="0" id="Image4" onmouseover="MM_swapImage('Image4','','images/mixed-on.gif',1)" onmouseout="MM_swapImgRestore()" /></a></td>
    <td width="100"><a href="fiber.html"><img src="images/fiber-off.gif" alt="Joan Wolfer Fiber Art" width="100" height="46" border="0" id="Image5" onmouseover="MM_swapImage('Image5','','images/fiber-on.gif',1)" onmouseout="MM_swapImgRestore()" /></a></td>
    <td width="122"><a href="artist.html"><img src="images/about-artist-off.gif" alt="Joan Wolfer Art" width="122" height="46" border="0" id="Image6" onmouseover="MM_swapImage('Image6','','images/about-artist-on.gif',1)" onmouseout="MM_swapImgRestore()" /></a></td>
    <td width="119"><a href="inquiries.html"><img src="images/contact-off.gif" alt="Joan Wolfer Art" width="115" height="46" border="0" id="Image7" onmouseover="MM_swapImage('Image7','','images/contact-on.gif',1)" onmouseout="MM_swapImgRestore()" /></a></td>
    <td width="2"></td>
  </tr>
</table>


  <!-- <img src="images/nav-holder.gif" width="825" height="34" />-->
  </div><!-- end nav div -->
  <table width="950" border="0" cellspacing="0" cellpadding="0">
  <tr>
    <td width="301"><div class="homepageleft" id="left">
     
      
      <h1>&nbsp;</h1>
      <h1>Fiberart By Wolfer</h1>
     
      <p>Boulder Colorado artist Joan Wolfer creates one-of-a-kind Fiberart Wall Hangings and unique floor standing Pole People. A member of the Boulder Colorado Arts Association, Joan has won many awards for her artwork. She shows her work in galleries and juried art shows around the country but her pieces can be seen in Boulder. Joan uses colorful yarns, threads, paint, sculpting, paper and wood to create embellished mixed media fiberart canvaswork Wall Hangings and Pole People. </p>
      <p>&nbsp;</p>
      <p/>

        
    </div></td>
    <td width="636"><div class="homepageright" id="right" >
     <table width="0" border="0" cellspacing="0" cellpadding="5">
  <tr>
    <td width="196" height="601" style="padding-left:10px;"><p>&nbsp;</p>
      <p>&nbsp;</p>
      <p>Canvaswork
      </p>
      <p><a href="canvaswork1.html"><img src="images/1.Time-LineForIndex.jpg" width="190" height="414" border="0" /></a></p>
      <p>&nbsp;</p>
      <p>&nbsp;</p></td>
    <td width="220" style="padding-left:5px;"><p>Pole People</p>
      <p><a href="pole1.html"><img src="images/pole/Palette-PreferenceLarge.jpg" width="220" height="414" border="0" /></a></p></td>
    <td width="188"><p>&nbsp;</p>
      <p>&nbsp;</p>
      <p>Mixed Media</p>
      <p><a href="mixed.html"><img src="images/mixed/The-GardenSmall.jpg" width="150" height="191" border="0" /></a></p>
      <p>Small Canvaswork</p>
      <p><a href="mixed2.html"><img src="images/mixed/Flowering-Moon.jpg" width="150" height="241" border="0" /></a></p></td>
  </tr>
</table>
    
    
    
     </div></td>
    <td width="13"><div class="homepageleft" id="gutter"></div><!--end gutter div--></td>
  </tr>
</table>
  <div id="footer">Email: <a href="mailto:joanwolfer@wildblue.net">joanwolfer@wildblue.net</a><span style="padding-left:49px;"> Phone: 303-449-7144</span>     <span style="padding-left:350px;">&copy;2012 FiberArt by Wolfer 
  : Joan Wolfer<br /><br />
Fiberart, fiber art, wall hangings, canvas work, mixed media, Joan Wolfer, Fiberart by Wolfer, fiber canvaswork</span></div><!-- end footer here-->
</div><!-- end layout div here-->




</body>
</html>
<title>Fiberart By Wolfer | Boulder, Colorado | Joan Wolfer | Fiber Canvaswork</title>


""",
   'www.sapphireskyfiberarts.com': 
    """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">


<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    
    <meta name="Generator" content="iWeb 3.0.4" />
    <meta name="iWeb-Build" content="local-build-20110924" />
    <meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7" />
    <meta name="viewport" content="width=700" />
    <title>Home</title>
    <link rel="stylesheet" type="text/css" media="screen,print" href="Home_files/Home.css" />
    <!--[if lt IE 8]><link rel='stylesheet' type='text/css' media='screen,print' href='Home_files/HomeIE.css'/><![endif]-->
    <!--[if gte IE 8]><link rel='stylesheet' type='text/css' media='screen,print' href='Media/IE8.css'/><![endif]-->
    <script type="text/javascript" src="Scripts/iWebSite.js"></script>
    <script type="text/javascript" src="Scripts/iWebImage.js"></script>
    <script type="text/javascript" src="Home_files/Home.js"></script>
  </head>
  <body style="background: rgb(0, 0, 0); margin: 0pt; " onload="onPageLoad();">
    <div style="text-align: center; ">
      <div style="margin-bottom: 0px; margin-left: auto; margin-right: auto; margin-top: 0px; overflow: hidden; position: relative; word-wrap: break-word;  text-align: left; width: 700px; " id="body_content">
        <div style="background: transparent url(Home_files/backgroundimage_1.jpg) no-repeat scroll center center; width: 700px; ">
          <div style="float: left; margin-left: 0px; position: relative; width: 700px; z-index: 0; " id="nav_layer">
            <div style="height: 0px; line-height: 0px; " class="bumper"> </div>
            <div style="clear: both; height: 0px; line-height: 0px; " class="spacer"> </div>
          </div>
          <div style="height: 150px; margin-left: 0px; position: relative; width: 700px; z-index: 10; " id="header_layer">
            <div style="height: 0px; line-height: 0px; " class="bumper"> </div>
            <div style="height: 1px; width: 630px;  height: 1px; left: 35px; position: absolute; top: 3px; width: 630px; z-index: 1; " class="tinyText">
              <div style="position: relative; width: 630px; ">
                <img src="Home_files/shapeimage_1.jpg" alt="" style="height: 1px; left: 0px; position: absolute; top: 0px; width: 630px; " />
              </div>
            </div>
            


            <div style="height: 121px; width: 704px;  height: 121px; left: -2px; position: absolute; top: 31px; width: 704px; z-index: 1; " class="tinyText style_SkipStroke">
              <img src="Home_files/Screen%20shot%202011-04-27%20at%2010.04.08%20AM.jpg" alt="" style="border: none; height: 121px; width: 704px; " />
            </div>
          </div>
          <div style="margin-left: 0px; position: relative; width: 700px; z-index: 5; " id="body_layer">
            <div style="height: 0px; line-height: 0px; " class="bumper"> </div>
            <div id="id1" style="height: 49px; left: 42px; position: absolute; top: 9px; width: 615px; z-index: 1; " class="style_SkipStroke_1 shape-with-text">
              <div class="text-content style_External_615_49 vertical-align-middle-middlebox" style="padding: 0px; ">
                <div class="style vertical-align-middle-innerbox">
                  <p style="padding-bottom: 0pt; padding-top: 0pt; " class="paragraph_style"><a class="class1" title="" href="">Home  </a>      <a class="class2" title="My_Albums/My_Albums.html" href="My_Albums/My_Albums.html">Albums  </a>      <a class="class3" title="Alpacas.html" href="Alpacas.html">Alpacas </a>       <a class="class4" title="Shows.html" href="Shows.html">Shows</a></p>
                </div>
              </div>
            </div>
            


            <div style="height: 187px; width: 317px;  height: 187px; left: 338px; position: absolute; top: 74px; width: 317px; z-index: 1; " class="tinyText style_SkipStroke_2 stroke_0">
              <img src="Home_files/Curry-Elrod%20Hat.jpg" alt="" style="border: none; height: 188px; width: 317px; " />
            </div>
            


            <div style="height: 407px; width: 266px;  height: 407px; left: 43px; position: absolute; top: 74px; width: 266px; z-index: 1; " class="tinyText style_SkipStroke_2 stroke_0">
              <img src="Home_files/img_0415%20%282%29cropped.jpg" alt="" style="border: none; height: 407px; width: 267px; " />
            </div>
            


            <div id="id2" style="height: 172px; left: 338px; position: absolute; top: 317px; width: 317px; z-index: 1; " class="style_SkipStroke_1 shape-with-text">
              <div class="text-content graphic_textbox_layout_style_default_External_317_172" style="padding: 0px; ">
                <div class="graphic_textbox_layout_style_default">
                  <p style="padding-top: 0pt; " class="paragraph_style_1">Sapphire Sky Alpacas and Fiber Arts is a small  family run organic haven just west of Denver, Colorado. We have been caring for alpacas since  1998 and each of our crew of 7 is an adored family member. <br /></p>
                </div>
              </div>
            </div>
            


            <div id="id3" style="height: 117px; left: 42px; position: absolute; top: 481px; width: 617px; z-index: 1; " class="style_SkipStroke_1 shape-with-text">
              <div class="text-content graphic_textbox_layout_style_default_External_617_117" style="padding: 0px; ">
                <div class="graphic_textbox_layout_style_default">
                  <p style="padding-bottom: 0pt; padding-top: 0pt; " class="paragraph_style_1">Every Spring, the alpaca’s winter coats are shorn to give them more comfort during the summer months. This alpaca fiber is what I use to create my one of a kind felted art. I make each unique piece entirely by hand, and strive to embody in each work, the energy and special character of the alpaca from which the fiber originated.</p>
                </div>
              </div>
            </div>
            <div style="height: 598px; line-height: 598px; " class="spacer"> </div>
          </div>
          <div style="height: 150px; margin-left: 0px; position: relative; width: 700px; z-index: 15; " id="footer_layer">
            <div style="height: 0px; line-height: 0px; " class="bumper"> </div>
            <div style="height: 133px; width: 602px;  height: 133px; left: 49px; position: absolute; top: 8px; width: 602px; z-index: 1; " class="tinyText style_SkipStroke_3 stroke_1">
              <img src="Home_files/Screen%20shot%202011-04-27%20at%2010.26.59%20AM.jpg" alt="" style="border: none; height: 134px; width: 602px; " />
            </div>
            


            <div class="tinyText" style="height: 41px; left: 212px; position: absolute; top: 53px; width: 270px; z-index: 1; ">
              <img usemap="#map1" id="shapeimage_2" src="Home_files/shapeimage_2.png" style="border: none; height: 47px; left: -3px; position: absolute; top: -3px; width: 276px; z-index: 1; " alt="" title="" /><map name="map1" id="map1"><area href="mailto:deannace@earthlink.net?subject=Sapphire%20Sky%20Info" title="mailto:deannace@earthlink.net?subject=Sapphire Sky Info" alt="mailto:deannace@earthlink.net?subject=Sapphire%20Sky%20Info" coords="3, 3, 273, 44" /></map>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>""",
    'www.sapphireskyfiberarts.com/Shows.html':
    """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">


<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    
    <meta name="Generator" content="iWeb 3.0.4" />
    <meta name="iWeb-Build" content="local-build-20110924" />
    <meta http-equiv="X-UA-Compatible" content="IE=EmulateIE7" />
    <meta name="viewport" content="width=700" />
    <title>Shows</title>
    <link rel="stylesheet" type="text/css" media="screen,print" href="Shows_files/Shows.css" />
    <!--[if lt IE 8]><link rel='stylesheet' type='text/css' media='screen,print' href='Shows_files/ShowsIE.css'/><![endif]-->
    <!--[if gte IE 8]><link rel='stylesheet' type='text/css' media='screen,print' href='Media/IE8.css'/><![endif]-->
    <script type="text/javascript" src="Scripts/iWebSite.js"></script>
    <script type="text/javascript" src="Scripts/iWebImage.js"></script>
    <script type="text/javascript" src="Shows_files/Shows.js"></script>
  </head>
  <body style="background: rgb(0, 0, 0); margin: 0pt; " onload="onPageLoad();">
    <div style="text-align: center; ">
      <div style="margin-bottom: 0px; margin-left: auto; margin-right: auto; margin-top: 0px; overflow: hidden; position: relative; word-wrap: break-word;  text-align: left; width: 700px; " id="body_content">
        <div style="background: transparent url(Shows_files/backgroundimage_1.jpg) no-repeat scroll center center; width: 700px; ">
          <div style="float: left; margin-left: 0px; position: relative; width: 700px; z-index: 0; " id="nav_layer">
            <div style="height: 0px; line-height: 0px; " class="bumper"> </div>
            <div style="clear: both; height: 0px; line-height: 0px; " class="spacer"> </div>
          </div>
          <div style="height: 150px; margin-left: 0px; position: relative; width: 700px; z-index: 10; " id="header_layer">
            <div style="height: 0px; line-height: 0px; " class="bumper"> </div>
            <div style="height: 1px; width: 630px;  height: 1px; left: 35px; position: absolute; top: 3px; width: 630px; z-index: 1; " class="tinyText">
              <div style="position: relative; width: 630px; ">
                <img src="Shows_files/shapeimage_1.jpg" alt="" style="height: 1px; left: 0px; position: absolute; top: 0px; width: 630px; " />
              </div>
            </div>
            


            <div style="height: 121px; width: 704px;  height: 121px; left: -1px; position: absolute; top: 31px; width: 704px; z-index: 1; " class="tinyText style_SkipStroke">
              <img src="Shows_files/Screen%20shot%202011-04-27%20at%2010.04.08%20AM.jpg" alt="" style="border: none; height: 121px; width: 704px; " />
            </div>
          </div>
          <div style="margin-left: 0px; position: relative; width: 700px; z-index: 5; " id="body_layer">
            <div style="height: 0px; line-height: 0px; " class="bumper"> </div>
            <div id="id1" style="height: 57px; left: 36px; position: absolute; top: 68px; width: 630px; z-index: 1; " class="style_SkipStroke_1 shape-with-text">
              <div class="text-content style_External_630_57 vertical-align-middle-middlebox" style="padding: 0px; ">
                <div class="style vertical-align-middle-innerbox">
                  <p style="padding-bottom: 0pt; padding-top: 0pt; " class="paragraph_style">2011 Show Schedule</p>
                </div>
              </div>
            </div>
            


            <div style="height: 127px; width: 300px;  height: 127px; left: 199px; position: absolute; top: 132px; width: 300px; z-index: 1; " class="tinyText style_SkipStroke_2 stroke_0">
              <img src="Shows_files/IMG_3709.jpg" alt="" style="border: none; height: 127px; width: 300px; " />
            </div>
            


            <div id="id2" style="height: 54px; left: 44px; position: absolute; top: 9px; width: 613px; z-index: 1; " class="style_SkipStroke_3 shape-with-text">
              <div class="text-content graphic_textbox_layout_style_default_External_613_54" style="padding: 0px; ">
                <div class="graphic_textbox_layout_style_default">
                  <p style="padding-bottom: 0pt; padding-top: 0pt; " class="paragraph_style_1">                <a class="class1" title="Home.html" href="Home.html">Home</a>         <a class="class2" title="My_Albums/My_Albums.html" href="My_Albums/My_Albums.html">Albums</a>         <a class="class3" title="Alpacas.html" href="Alpacas.html">Alpacas</a>         <a class="class4" title="" href="">Shows</a></p>
                </div>
              </div>
            </div>
            


            <div id="id3" style="height: 315px; left: 154px; position: absolute; top: 266px; width: 394px; z-index: 1; " class="style_SkipStroke_3 shape-with-text">
              <div class="text-content graphic_textbox_layout_style_default_External_394_315" style="padding: 0px; ">
                <div class="graphic_textbox_layout_style_default">
                  <p style="padding-top: 0pt; " class="paragraph_style_2">May 20,21 &amp; 22 - National Alpaca Show<br /></p>
                  <p class="paragraph_style_2">                                   Denver, CO<br /></p>
                  <p class="paragraph_style_2">June 11 &amp; 12, 2011 - Estes Park Wool Market<br /></p>
                  <p class="paragraph_style_2">                                      Estes Park, Colorado<br /></p>
                  <p class="paragraph_style_2">August 13,14 - Salida Riverside Fine Arts <br /></p>
                  <p class="paragraph_style_2">                             Festival<span class="style_1"><br /></span></p>
                  <p class="paragraph_style_2">August 20,21 - Golden Fine Arts Festival<br /></p>
                  <p class="paragraph_style_2">September 3,4 &amp; 5 - Commonwheel Artists <br /></p>
                  <p class="paragraph_style_2">                        Co-Op Art Festival                             <br /></p>
                  <p style="padding-bottom: 0pt; " class="paragraph_style_2">October 1,2 - Taos Wool Festival</p>
                </div>
              </div>
            </div>
            


            <div style="height: 300px; width: 267px;  height: 300px; left: 215px; position: absolute; top: 651px; width: 267px; z-index: 1; " class="tinyText style_SkipStroke_2 stroke_0">
              <img src="Shows_files/img_0392%20%282%29cropped.jpg" alt="" style="border: none; height: 300px; width: 268px; " />
            </div>
            


            <div style="height: 133px; width: 602px;  height: 133px; left: 50px; position: absolute; top: 958px; width: 602px; z-index: 1; " class="tinyText style_SkipStroke_4 stroke_1">
              <img src="Shows_files/Screen%20shot%202011-04-27%20at%2010.26.59%20AM.jpg" alt="" style="border: none; height: 134px; width: 602px; " />
            </div>
            <div style="height: 947px; line-height: 947px; " class="spacer"> </div>
          </div>
          <div style="height: 150px; margin-left: 0px; position: relative; width: 700px; z-index: 15; " id="footer_layer">
            <div style="height: 0px; line-height: 0px; " class="bumper"> </div>
            <div class="tinyText" style="height: 41px; left: 214px; position: absolute; top: 59px; width: 270px; z-index: 1; ">
              <img usemap="#map1" id="shapeimage_2" src="Shows_files/shapeimage_2.png" style="border: none; height: 47px; left: -3px; position: absolute; top: -3px; width: 276px; z-index: 1; " alt="" title="" /><map name="map1" id="map1"><area href="mailto:deannace@earthlink.net?subject=Sapphire%20Sky%20Info" title="mailto:deannace@earthlink.net?subject=Sapphire Sky Info" alt="mailto:deannace@earthlink.net?subject=Sapphire%20Sky%20Info" coords="3, 3, 273, 44" /></map>
            </div>
          </div>
        </div>
      </div>
    </div>
  </body>
</html>

"""





}








myurl = 'http://www.handweaversofboulder.org/membergallery.html'
#mydict = create_member_dictionary(myurl)
#myi, myd = crawl_member_gallery(myurl)
#print "INDEX"
#print myi
#print "  "
#print "DICTIONARY"
#print myd
newpage = create_custom_gallery(myurl,['create', 'the', 'fOr'])

print newpage
#print myi
#print strip_html_tags(get_page(myurl))


