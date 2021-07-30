import requests
import datetime
import feedparser
import pandas as pd
import os
import logging
from goose3 import Goose
from goose3.text import StopWordsKorean
from gensim.summarization.summarizer import summarize

class newsScrap():
    def __init__(self): 
        print("Constructor")
        self._title = []
    def __del__(self): 
        print("Garbage Collection")

    def exec(self, keyword, day, country, news_room):
        print("Crawl")
        URL = news_room # you need to override this method
        
        res = requests.get(URL)
        if res.status_code == 200:
            datas = feedparser.parse(res.text).entries ## what is entries?
            
            for data in datas:
                self._title.append(data.title)

        else:
            print("No response")

    def setDataFrame(self):
        raw_data = {'title' : self._title}
        res = pd.DataFrame(raw_data)
        file_name = "./result.csv"
        if os.path.isfile(file_name):
            os.remove(file_name)
        res.to_csv(file_name)



class googleScrap(newsScrap):
    def __init__(self):
        newsScrap.__init__(self)
        self._time = []
        self._link = []
        self._summary = []
        self._source = []
        self._keyword = []
        self._DataFrame = None

    def exec(self, keyword, day, country = 'ko'): # Google News Feed parsing method

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
                try:
                    g = Goose({'stopwords_class':StopWordsKorean})
                    article = g.extract(url=url)
                    self._summary.append(article.cleaned_text[:500])
                    # self._summary.append(article.meta_description)
                    # self._summary.append(summarize(article.cleaned_text[:1500]))

                except:
                    self._summary.append(data.title)
                    pass
                                 
        else:
            print ('Google Search Error!!')
       
    def setDataFrame(self):
        raw_data = {
            'title' : self._title,
            'time' : self._time,
            'summarize' : self._summary,
            'link' : self._link,
            'source' : self._source,
            'keyword' : self._keyword
        }
        self._DataFrame = pd.DataFrame(raw_data)
    
    def createCSV(self, file_name):
        file = './' + file_name + '.csv'
        if os.path.isfile(file):
            os.remove(file)
        self._DataFrame.to_csv(file, encoding='utf-8-sig')

    def createHTML(self, file_name):
        file = './' + file_name + '.html'
        if os.path.isfile(file):
            os.remove(file)
        self._DataFrame.to_html(file, encoding='utf-8-sig') # use (escape=False) if you want to make URL tag in html

if __name__ == “__main__”
    today = googleScrap()
    today.exec('스마트팩토리', 1)
    today.setDataFrame()
    today.createHTML('result')
    del today