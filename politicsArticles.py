from selenium import webdriver
from pymongo import MongoClient
import json


path = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(path)


def linkExtractor(url,main_class,sub_class):
    links = []
    driver.get(url)
    paragraphs = driver.find_elements_by_xpath('//div[@class = "'+main_class+'"]')
    for paragraph in paragraphs:
        sections = paragraph.find_elements_by_class_name(sub_class)
        for section in sections:
            tag = section.find_elements_by_tag_name("a")
            for link in tag:
                if link.get_attribute("href") not in links:
                    links.append(link.get_attribute("href"))
    return links


def get(class_name):
    try:
        content = driver.find_element_by_class_name(class_name)
        content_string = content.text
    except:
        content_string = "Not Found"
        
    return content_string


def getInfo(class_name):
    try:
        info = driver.find_element_by_class_name(class_name)
        info_string = info.text
    
        items = info_string.split("Autore: ")
        date_section = items[0]
        author = items[1]
    
        raw_date = date_section.split()
        date_fields = raw_date[2:5]
        year = date_fields[2]
        explicit_month = date_fields[1]
        day = date_fields[0]

        if int(day) < 10:
            number_day = "0"+day
        else:
            number_day = day
    
        months = {"Gennaio": "01", "Febbraio": "02", "Marzo": "03", "Aprile": "04", "Maggio": "05", "Giugno": "06", "Luglio": "07", "Agosto": "08", "Settembre": "09", "Ottobre": "10", "Novembre": "11", "Dicembre": "12"}
        number_month = months[explicit_month]

        date = year+"/"+number_month+"/"+number_day
        
    except:
        author, date  = "Not Found", "Not Found"
        
    return author, date


def main():
    
    client = MongoClient("mongodb+srv://DataAcquisition:****@datascienceuninadb.om3a4.mongodb.net/DataScienceUninaDB?retryWrites=true&w=majority")
    db = client.datascience
    articles = db.politicsArticles
    
    for i in range(1,16):
        url = "https://www.termometropolitico.it/politica/page/"+str(i)
        links1 = linkExtractor(url,"medium-6 small-12 columns","main_title")
        links2 = linkExtractor(url,"medium-6 small-12 columns","large_title")
        links3 = linkExtractor(url,"medium-4 small-12 columns","medium_title")
    
        all_links = links1+links2+links3    #each page has 3 types of links: a main one, two medium ones, and a bunch of smaller ones. all_links is a list that contains all of them.

        for link in all_links:
            print("currently reading",link)
            driver.get(link)

            title = get("single_title")
            excerpt = get("single_excerpt")
            author, date = getInfo("single_info")
            body = get("general-text")

            article = {}

            article["title"] = title
            article["excerpt"] = excerpt
            article["author"] = author
            article["date"] = date
            article["body"] = body
        
            #articles.insert_one(article)
            
            articleJson = json.dumps(article, indent = 2)
            print(articleJson)
            
main()

