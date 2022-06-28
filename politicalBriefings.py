from selenium import webdriver
from pymongo import MongoClient
import json


path = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(path)


for i in range(441,442):
    client = MongoClient("mongodb+srv://DataAcquisition:****@datascienceuninadb.om3a4.mongodb.net/DataScienceUninaDB?retryWrites=true&w=majority")
    db = client.datascience
    documents = db.politicalBriefings
    
    URL = "https://www.camera.it/leg18/410?idSeduta="+str(i)+"&tipo=stenografico"
    driver.get(URL)
    transcript = driver.find_element_by_class_name("stenografico")
    transcript_string = transcript.text

    items = transcript_string.split("\n")
    date_line = items[2]
    raw_date = date_line.split()
    date_fields = raw_date[5:8]
    
    year = date_fields[2]
    explicit_month = date_fields[1]
    day = date_fields[0]
    
    if int(day) < 10:
        number_day = "0"+day
    else:
        number_day = day
    
    months = {"gennaio": "01", "febbraio": "02", "marzo": "03", "aprile": "04", "maggio": "05", "giugno": "06", "luglio": "07", "agosto": "08", "settembre": "09", "ottobre": "10", "novembre": "11", "dicembre": "12"}
    number_month = months[explicit_month]

    date = year+"/"+number_month+"/"+number_day
        
    document = {}
        
    document["date"] = date
    document["body"] = transcript_string
    
    documentJson = json.dumps(document, indent = 2)
    print(documentJson)
    
    #documents.insert_one(document)
        

