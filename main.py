# License : MIT
# Project : News Crawling using specific keywords
# Develop : Seunghwan Lee
# Version : 1. 1. 2
# Date    : 21-08-11

 #-*- coding: utf-8 -*- 
import requests
import datetime
import feedparser
import pandas as pd
import os
import logging
from goose3 import Goose
from goose3.text import StopWordsKorean
from gensim.summarization.summarizer import summarize
import warnings

# To Ignore warning sign
warnings.filterwarnings('ignore')


# Class :
class newsScrap():
    """Main Class related News Crawl"""

    def __init__(self): 
        print("Constructor")
        self._title = []
    def __del__(self): 
        print("Garbage Collection")

    """Get Webpage response method
        @param keyword : keyword to look for news
        @param day : how many days ago from today
        @param country : 2 types ["ko" || "en"]
        @param news_room : RSS feed list
    """
    def eccess(self, news_room):
        print("Crawl start")
        URL = news_room # you need to override this method
        
        res = requests.get(URL)
        if res.status_code == 200:
            datas = feedparser.parse(res.text).entries ## what is entries?
            
            for data in datas:
                self._title.append(data.title)

        else:
            print("No response")


    """Set data frame & change format & save (can override)"""
    def setDataFrame(self):
        raw_data = {'title' : self._title}
        res = pd.DataFrame(raw_data)
        file_name = "./result.csv"
        if os.path.isfile(file_name):
            os.remove(file_name)
        res.to_csv(file_name)



class googleScrap(newsScrap):
    """Extend NewsScrap class to use google news feed
    @param _time : the time news writed
    @param _link : news link
    @param _summary : news context
    @param _source : news source (ex. chosun, jungang...)
    @param _keyword : title keyword(we are looking for)
    @param _dataFrame : dataframe for changing format (.html, .csv...)
    """
    def __init__(self):
        newsScrap.__init__(self)
        self._time = []
        self._link = []
        self._summary = []
        self._source = []
        self._keyword = []
        self._dataFrame = None
        self._footNote = {}

    def eccess(self, keyword, day, country = 'ko'): # Google News Feed parsing method

        print ('Google News Cron Start: ' + datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
        URL = 'https://news.google.com/rss/search?q={}+when:{}d'.format(keyword, day)
        
        if country == 'en':
            URL += '&hl=en-NG&gl=NG&ceid=NG:en'
        elif country == 'ko':
            URL += '&hl=ko&gl=KR&ceid=KR:ko'

        res = requests.get(URL)
        if res.status_code == 200:
            datas = feedparser.parse(res.text).entries
            
            for data in datas:
                self._title.append(data.title)
                self._time.append(data.published)
                self._source.append(data.source.title)
                self._keyword.append(keyword)   
                self._link.append(data.link)
                try: # merge with company version
                    g = Goose({'stopwords_class':StopWordsKorean})
                    article = g.extract(url=URL)
                    self._summary.append(article.cleaned_text[:500])
                    # self._summary.append(article.meta_description)
                    # self._summary.append(summarize(article.cleaned_text[:1500]))

                except:
                    self._summary.append(data.title)
                    pass
                                 
        else:
            print ('Google Search Error!!')

    def addFootNote(self, keywords_li, country="kr"):
        for keywords in keywords_li:
            foot_link = "https://news.google.com/search?q={}".format(keywords)
        if country == 'en':
            foot_link += '&hl=en-NG&gl=NG&ceid=NG:en'
        elif country == 'ko':
            foot_link += '&hl=ko&gl=KR&ceid=KR:ko'
        self._footNote.update({keywords : foot_link})
       
    def setDataFrame(self):
        raw_data = {
            'title' : self._title,
            'time' : self._time,
            'summarize' : self._summary,
            'link' : self._link,
            'source' : self._source,
            'keyword' : self._keyword
        }
        self._dataFrame = pd.DataFrame(raw_data)
    
    def createCSV(self, file_name):
        file = './' + file_name + '.csv'
        if os.path.isfile(file):
            os.remove(file)
        self._dataFrame.to_csv(file, encoding='utf-8-sig')

    def createHTML(self, file_name):
        file = './' + file_name + '.html'
        if os.path.isfile(file):
            os.remove(file)
        self._dataFrame.to_html(file, encoding='utf-8-sig') # use (escape=False) if you want to make URL tag in html

    def appendFootNode(self, file_name):
        # 마크업 링크를 만든다
        markup = ""
        # ./{file_name}.html에 추가로 입력한다.
        with open("./{}.html".format(file_name), "a") as file:
            file.write(markup)
            file.close()
        
if __name__ == "__main__":
    today = googleScrap()
    today.eccess('smartfactory', 1)
    today.setDataFrame()
    today.createHTML('result')
    del today