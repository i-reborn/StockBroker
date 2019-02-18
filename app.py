import cherrypy

import os

import zipfile

import csv

import redis

import json

import urllib.request

import config

from datetime import date, datetime, timedelta

from jinja2 import Environment, FileSystemLoader

# GET CURRENT DIRECTORY
CUR_DIR = os.path.dirname(os.path.abspath(__file__))
env=Environment(loader=FileSystemLoader(CUR_DIR),trim_blocks=True)


# Create a redis client. This file is generally encrypted

redisClient = redis.StrictRedis(host=config.host,

                                port=config.port,

                                # user= config.db,
                                db=config.db)#,
                                
                                # password=config.password)
       
class Controller(object):
    @cherrypy.expose 
    def index(self):
        template = env.get_template('index.html')
        # RENDER TEMPLATE PASSING IN DATA
        return template.render( stockList=self.get_stockList())

    # HELPER FUNCTION TO RETURN STOCK LIST
    def get_stockList(self):
        
        stockList=[]
        for index,var in enumerate(range (self.json())):
            obj={}
            obj['Name']=redisClient.hget(index,'SC_NAME').decode('utf-8')
            obj['Code']=redisClient.hget(index,'SC_CODE').decode('utf-8')
            obj['Open']=redisClient.hget(index,'OPEN').decode('utf-8')
            obj['High']=redisClient.hget(index,'HIGH').decode('utf-8')
            obj['Low']=redisClient.hget(index,'LOW').decode('utf-8')
            obj['Close']=redisClient.hget(index,'CLOSE').decode('utf-8')
            stockList.append(obj)
        return stockList
 
    def json(self):
    
    
        # from pprint import pprint

        #This function gets today's date in required format

        yesterday= date.today() #- timedelta(1)

        yesterday = yesterday.strftime("%d%m%y") 

        print(yesterday)

        url = 'https://www.bseindia.com/download/BhavCopy/Equity/EQ'+yesterday+'_CSV.ZIP' 

        urllib.request.urlretrieve(url, './EQ'+yesterday+'_CSV.ZIP') 

        

        # This is the csv extraction from zip part

        zip_ref = zipfile.ZipFile('./EQ'+yesterday+'_CSV.ZIP', 'r')

        zip_ref.extractall('./')

        zip_ref.close()

        

        # This is to read csv in python and write it into a JSON file
        filename = './EQ'+yesterday+'.csv'

        csvfile = open(filename, 'r+')

        fieldnames=csvfile.readline()

        fieldnames=fieldnames[:-1]

        fieldnames = fieldnames.split(',')

        reader = csv.DictReader( csvfile, fieldnames)

        # here we insert data to redis db after deleting previous data

        redisClient.flushall()

        redisClient.set(str(yesterday),1)

        for index,row in  enumerate(reader):
                redisClient.hset(index,'SC_NAME', row['SC_NAME'])
                redisClient.hset(index, 'SC_CODE' , row['SC_CODE'])
                redisClient.hset(index, 'OPEN' ,row['OPEN'])
                redisClient.hset(index, 'HIGH', row['HIGH'])
                redisClient.hset(index, 'LOW', row['LOW'])
                redisClient.hset(index, 'CLOSE', row['CLOSE'])
                counter=index+1
        return counter

if __name__ == '__main__':
    conf={
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static':{
            'tools.staticdir.on': True,
            'tools.staticdir.dir': '.\\public',
        }
    }
    cherrypy.quickstart(Controller(),'/',conf)
  
