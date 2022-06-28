from selenium import webdriver
from pymongo import MongoClient
import re
import random
import json

def randomizer ():
    number = 100000000*random.random()
    return "A"+str(round(number))

def pageReverser (currentPage,maxPage):
    return (maxPage - currentPage)

def getUlr (driver,classToFind):
    links = []
    paragraphs = driver.find_elements_by_xpath('//div[@class = "'+classToFind+'"]')
    for paragraph in paragraphs:
        tag = paragraph.find_elements_by_tag_name("a")
        for link in tag:
            if(link.get_attribute("href") not in links):
                links.append(link.get_attribute("href"))
    return links

def dateCleaner (date):
    cleanDate = date.replace(",","")
    dateDic = {"JAN": "01", "FEB": "02", "MAR": "03", "APR": "04", "MAY": "05", "JUN": "06", "JUL": "07", "AUG": "08", "SEP": "09", "OCT": "10", "NOV": "11", "DEC": "12"}
    dateDicAlt = {"JANUARY": "01", "FEBRUARY": "02", "MARCH": "03", "APRIL": "04", "MAY": "05", "JUNE": "06", "JULY": "07", "AUGUST": "08", "SEPTEMBER": "09", "OCTOBER": "10", "NOVEMBER": "11", "DECEMBER": "12"}

    dateFields = cleanDate.split(" ")
    if ("Updated" in cleanDate):
        dateFields[0] = dateFields[5]
        dateFields[1] = dateFields[6]
        dateFields[2] = dateFields[7]
    if len(dateFields[1]) == 1:
        dateFields[1] = "0"+dateFields[1]
    if ((dateFields[0]).upper() in dateDicAlt.keys()):
        dateFields[0] = dateDicAlt[(dateFields[0]).upper()]
    elif ((dateFields[0]).upper() in dateDic.keys()):
        dateFields[0] = dateDic[(dateFields[0]).upper()]
    returnDate = dateFields[2]+"/"+dateFields[0]+"/"+dateFields[1]
    return returnDate

class Article:
    def __init__ (self,url,driver, titleTag, subTitleTag, dateTag, authorTag, bodyTag):
        self.driver = driver
        self.url = url
        self.driver.get(self.url)
        self.titleTag = titleTag
        self.subTitleTag = subTitleTag
        self.dateTag = dateTag
        self.authorTag = authorTag
        self.bodyTag = bodyTag

    def getBody (self):
        bodyText = ''
        try:
            body = self.driver.find_elements_by_xpath('//div[@class = "'+self.bodyTag+'"]')
            for par in body:
                bodyText = bodyText + "\n" + par.text
        except:
            try:
                body = self.driver.find_elements_by_xpath('//div[@class = "text"]')
                for par in body:
                    bodyText = bodyText + "\n" + par.text
            except:
                print("Cannot find body for :" + self.url)
                bodyText = "NOT_FOUND"
        if bodyText == '':
            bodyText = "NOT_FOUND"
        return bodyText

    def getDate(self):
        date = 'NOT_FOUND'
        try:
            date = dateCleaner((self.driver.find_element_by_class_name(self.dateTag)).text)
        except:
            print("Could not find date for " + self.url)
        return date

    def getTile(self):
        title = 'NOT_FOUND'
        try:
            title = (self.driver.find_element_by_class_name(self.titleTag)).text
        except:
            print("Could not find title for " + self.url)
        return title

    def getSubTitle(self):
        subtitle = 'NOT_FOUND'
        try:
            subtitle = (self.driver.find_element_by_class_name(self.subTitleTag)).text
        except:
            pass
        return subtitle

    def getAuthors(self):
        authors = []
        try:
            listOfAuthors = self.driver.find_elements_by_class_name(self.authorTag)
        except:
            print("Could not find authors for " + self.url)
        for auth in listOfAuthors:
            authors.append(auth.text)
        return authors

def pewResearchExtractor (pageNumber,tableName,reverse):
    print ("Starting program main...")
    if not isinstance(pageNumber, int) or pageNumber < 1:
        print("Page number must be a non zero integer. Aborting.")
        return

    articleNumber = 0
    dischargedNumber = 0
    data = {}
    path = "C:/Users/emanu/OneDrive/Desktop/chromedriver_win32/chromedriver.exe"
    driver = webdriver.Chrome(path)

    for currentPage in range(0,pageNumber):
        currentPage = currentPage+1
        mainUrl = "https://www.pewresearch.org/publications/page/"+str(currentPage)+ "/"
        print("Currently reading: "+mainUrl)
        driver.get(mainUrl)
        articleUrl = getUlr(driver,"header normal")
        for url in articleUrl:
            articleNumber = articleNumber + 1
            print("Currently reading article: "+url)
            driver.get(url)
            article = Article(url,driver,titleTag="post-title",subTitleTag="post-subtitle",dateTag="date",authorTag="author",bodyTag="ui text container post-content")
            data["body"] = article.getBody()
            data["title"] = article.getTile()
            data["authors"] = article.getAuthors()
            data["date"] = article.getDate()
            data["url"] = article.url
            data["_id"] = randomizer()
            subTitle = article.getSubTitle()
            if (subTitle != 'NOT_FOUND'):
                data["subtitle"] = article.getSubTitle()
            if (data["body"] == "NOT_FOUND"):
                dischargedNumber = dischargedNumber + 1
                continue
            else:
                tableName.insert_one(data)
    print ("Done! "+str(articleNumber)+" read, "+str(dischargedNumber)+" discharged.")

def cnnExtractor (pageNumber,tableName,reverse):
    print ("Starting program main...")
    if not isinstance(pageNumber, int) or pageNumber < 1:
        print("Page number must be a non zero integer. Aborting.")
        return

    articleNumber = 0
    dischargedNumber = 0
    data = {}
    path = "C:/Users/emanu/OneDrive/Desktop/chromedriver_win32/chromedriver.exe"
    driver = webdriver.Chrome(path)

    for currentPage in range(0,pageNumber):
        currentPage = currentPage+1
        mainUrl = "https://edition.cnn.com/article/sitemap-2020-"+str(11-currentPage)+".html"
        driver.get(mainUrl)
        articleUrl = getUlr(driver,"sitemap-entry")
        for url in articleUrl:
            articleNumber = articleNumber + 1
            print("Currently reading article: "+url)
            driver.get(url)
            article = Article(url,driver,titleTag="pg-headline",subTitleTag="zn-body__paragraph speakable",dateTag="update-time",authorTag="metadata__byline__author",bodyTag="zn-body__paragraph")
            data["body"] = article.getBody()
            data["title"] = article.getTile()
            data["authors"] = article.getAuthors()
            data["date"] = article.getDate()
            data["url"] = article.url
            data["_id"] = randomizer()
            subTitle = article.getSubTitle()
            if (subTitle != 'NOT_FOUND'):
                data["subtitle"] = article.getSubTitle()
            if (data["body"] == "NOT_FOUND"):
                dischargedNumber = dischargedNumber + 1
                continue
            else:
                tableName.insert_one(data)
    print ("Done! "+str(articleNumber)+" read, "+str(dischargedNumber)+" discharged.")

def dbPrinter(numberOfPages,dbName,tableName,extractFunction):
    client = MongoClient("mongodb+srv://****:****@datascienceuninadb.om3a4.mongodb.net/DataScienceUninaDB?retryWrites=true&w=majority")
    db = client[dbName]
    articles = db[tableName]
    extractFunction(pageNumber = numberOfPages,tableName = articles,reverse = False)

dbPrinter(numberOfPages = 10, dbName = "datascience",tableName = "cnnArticles", extractFunction = cnnExtractor)
 