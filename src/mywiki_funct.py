import os
import time
import re
import logging
import csv
import codecs
import xml.etree.ElementTree as ET
import sqlite3

# Fonctions pour le traitement des fichiers xml de wikipedia
## retrieve article lists
def strip_tag_name(t):
    """strip_tag_name fonction pour couper la balise du fichier xml dans un format plus lisible

    Args:
        t (str): balise xml

    Returns:
        str: balise xml dans un format plus lisible
    """
    idx = k = t.rfind("}")
    if idx != -1:
        t = t[idx + 1:]
    return t

def hms_string(sec_elapsed):
    """hms_string fonction pour convertir les secondes en heures, minutes et secondes

    Args:
        sec_elapsed : nombre de secondes

    Returns:
        str: nombre de secondes converti en heures, minutes et secondes pour affichage
    """
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)

def retrieve_article_info(PATH_WIKI_XML, FILENAME_WIKI, FILENAME_ARTICLES, FILENAME_REDIRECT, FILENAME_TEMPLATE, encoding='utf-8'):
    """retrieve_article_info cette fonction permet de faire la liste des articles, des redirections et des templates 
    à partir du fichier xml d'une version de wikipedia
    fonction adaptée de https://github.com/jeffheaton/article-code/

    Args:
        PATH_WIKI_XML (str): chemin du dossier du xml de wikipedia
        FILENAME_WIKI (str): nom du fichier xml de wikipedia
        FILENAME_ARTICLES (str): nom du fichier csv pour les articles
        FILENAME_REDIRECT (str): nom du fichier csv pour les redirections
        FILENAME_TEMPLATE (str): nom du fichier csv pour les templates
    """
    pathWikiXML = os.path.join(PATH_WIKI_XML, FILENAME_WIKI)
    pathArticles = os.path.join(PATH_WIKI_XML, FILENAME_ARTICLES)
    pathArticlesRedirect = os.path.join(PATH_WIKI_XML, FILENAME_REDIRECT)
    pathTemplateRedirect = os.path.join(PATH_WIKI_XML, FILENAME_TEMPLATE)

    totalCount = 0
    articleCount = 0
    redirectCount = 0
    templateCount = 0
    title = None
    start_time = time.time()

    with codecs.open(pathArticles, "w", encoding) as articlesFH, \
            codecs.open(pathArticlesRedirect, "w", encoding) as redirectFH, \
            codecs.open(pathTemplateRedirect, "w", encoding) as templateFH:
        articlesWriter = csv.writer(articlesFH, quoting=csv.QUOTE_MINIMAL)
        redirectWriter = csv.writer(redirectFH, quoting=csv.QUOTE_MINIMAL)
        templateWriter = csv.writer(templateFH, quoting=csv.QUOTE_MINIMAL)

        articlesWriter.writerow(['id', 'title', 'redirect'])
        redirectWriter.writerow(['id', 'title', 'redirect'])
        templateWriter.writerow(['id', 'title'])

        for event, elem in ET.iterparse(pathWikiXML, events=('start', 'end')):
            tname = strip_tag_name(elem.tag)

            if event == 'start':
                if tname == 'page':
                    title = ''
                    id = -1
                    redirect = ''
                    inrevision = False
                    ns = 0
                elif tname == 'revision':
                    # Do not pick up on revision id's
                    inrevision = True
            else:
                if tname == 'title':
                    title = elem.text
                elif tname == 'id' and not inrevision:
                    id = int(elem.text)
                elif tname == 'redirect':
                    redirect = elem.attrib['title']
                elif tname == 'ns':
                    ns = int(elem.text)
                elif tname == 'page':
                    totalCount += 1

                    if ns == 10:
                        templateCount += 1
                        templateWriter.writerow([id, title])
                    elif len(redirect) > 0:
                        articleCount += 1
                        redirectWriter.writerow([id, title, redirect])
                    else:
                        redirectCount += 1
                        articlesWriter.writerow([id, title, redirect])

                    # if totalCount > 100000:
                    #  break

                    if totalCount > 1 and (totalCount % 100000) == 0:
                        print("{:,}".format(totalCount))

                elem.clear()

    elapsed_time = time.time() - start_time

    print("Total pages: {:,}".format(totalCount))
    print("Template pages: {:,}".format(templateCount))
    print("Article pages: {:,}".format(articleCount))
    print("Redirect pages: {:,}".format(redirectCount))
    print("Elapsed time: {}".format(hms_string(elapsed_time)))
    
    
## retrieve article text from wikiextractor output

def reader_txt(file:str):
    """reader_txt reads a file and returns the text within it

    Args:
        file (str): path of the file

    Returns:
        str: text withing the file
    """
    with open(file, 'r') as filer:
        return filer.read()
    
def splitter_txt(text:str, separator="</doc>"):
    """splitter_txt splits a text into a list of strings using a separator

    Args:
        text (str): text to be split
        separator (str): separator to be used

    Returns:
        list: list of strings
    """
    return text.split(separator)

def get_id_title_url(text:str):
    """get_id_title gets the id and title of an article from the text

    Args:
        text (str): text to be processed

    Returns:
        str: id of the article
        str: title of the article
    """
    # patterns
    id_match = re.search(r'id="(\d+)"', text)
    title_match = re.search(r'title="([^"]+)"', text)
    url_match = re.search(r'url="(https?://[^\s<>"]+)"', text)
    
    id_value = None
    title = None
    url_value = None
    
    if id_match:
        id_value = id_match.group(1)
        
    if title_match:
        title = title_match.group(1)
        
    if url_match:
        url_value = url_match.group(1)
        
    return {'id':id_value, 'title':title, 'url':url_value}

def get_text(text:str):
    """get_text gets the text of an article from the text

    Args:
        text (str): text to be processed

    Returns:
        str: text of the article
    """
    # patterns
    return text.split('>')[1]
    
def export_text_with_id(text:str, id, destination:str):
    """export_text_with_id exports the text to a file with the id as name

    Args:
        text (str): text to be exported
        id (str): id of the article
        destination (str): path of the folder to save the file
    """
    with open(destination+'/'+id+'.txt', 'w') as filew:
        filew.write(text)
        
def export_DB_text_with_id(text:str, id, title, url, db_name):
    """export_text_with_id exports the text to the database with the id as name

    Args:
    text (str): text to be exported
    id (str): id of the article
    title (str): title of the article
    url (str): URL of the article
    db_name (str): path of the database
    """
    
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Insert data into the table
    c.execute("INSERT INTO articles (id, title, url, text) VALUES (?, ?, ?, ?)", (id, title, url, text))

    # Save (commit) the changes
    conn.commit()

    # Close the connection
    conn.close()
        
def wrapper_splitter_txt(source: str, destination:str, separator="</doc>"):
    """wrapper_splitter_txt wrapper function to split a file into multiple files

    Args:
        source (str): file to be split
        separator (str): separator to be used
        destination (str): path of the folder to save the files
    """
    text = reader_txt(source)
    sptext = splitter_txt(text, separator)
    for i, txt in enumerate(sptext[:-1]):
        dict_text = get_id_title_url(txt)
        text = get_text(txt)
        export_DB_text_with_id(text, dict_text['id'], dict_text['title'], dict_text['url'],  destination)
    
def looper_wrapper_splitter_txt(source: str, destination:str, separator="</doc>"):
    """looper_wrapper_splitter_txt loops through the files in a folder and splits them into multiple files

    Args:
        source (str): folder to be split
        separator (str): separator to be used
        destination (str): path of the folder to save the files
    """
    for folder in os.listdir(source):
        print(f'Folder {folder} started')
        for file in os.listdir(source+'/'+folder):
            print(f'file {file} started')
            wrapper_splitter_txt(source+'/'+folder+'/'+file, destination, separator)
            print(f'file {file} done')
    print('All done ! :3') 


## autres fonctions utilitaires
def lovely_tree_file(startpath):
    """lovely_tree_file makes a tree of the files in a folder

    Args:
        startpath (str): folder to look for files
    """
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))