# -*- coding: utf-8 -*-
"""
Created on Wen Mar 21 18:21:37 2018
Func:使用爬虫下载来读电子书
PGM:python_learning_crawler_laidu_new.py
@author:benbendemo
@email:xc0910@hotmail.com
"""

import requests
from bs4 import BeautifulSoup
import re
import datetime
import profile
import pdfkit

PGMname = 'PGM:python_learning_crawler_laidu_new'

class Crawler(object):
    '''
    1. 定义爬虫基类
    2. 定义SESSION、HEADER、BASE_URL等类参数
    '''
    SESSION = requests.Session()
    LOGIN_URL = 'http://laidu.co/login'
    HEADER = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) \
              AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
    
    @classmethod
    def login_with_session(cls):
        '''
        由于待爬取网站需要登陆，使用SESSION.post方法进行登陆验证
        '''
        
        payload = {
                   'email': 'XXXXXXX', 
                   'password': 'XXXXXXXX',
                   '_token': cls.get_xsrf()
                   }
        cls.SESSION.post(url=cls.LOGIN_URL, data=payload)
        return cls.SESSION
    
    @classmethod
    def get_xsrf(cls):
        '''
        使用SESSION登陆前，需要先获取xsrf伪随机数
        '''
        
        response = cls.SESSION.get(url=cls.LOGIN_URL, headers=cls.HEADER)
        soup = BeautifulSoup(response.content, "html.parser")
        xsrf = soup.find('input', attrs={"name": "_token"}).get("value")
        print "---xsrf---:",xsrf
        return xsrf
    
    @classmethod
    def logoff_with_session(cls):
        '''
        爬取结束后，关闭SESSION
        '''
        
        cls.SESSION.close()
        
class Parse(Crawler):
    '''
    1. 继承Crawler类，定义页面解析类
    2. 定义BASE_URL、HTML_TEMPLATE和正则表达式类变量
    '''
    
    # 基地址
    BASE_URL = 'http://laidu.co'
    
    # html网页模版文件
    HTML_TEMPLATE = """
     <!DOCTYPE HTML>
     <html lang="en">
         <head>
             <meta charset="UTF-8">
             <meta content="text/html; charset=utf-8" http-equiv="Content-Type">
         </head>
         <body>
             {content}
         </body>
     </html>
     """
    
    # 定义html文本中匹配img标签的正则表达式
    IMG_PATTERN = "(<img .*?src=\")(.*?\.png|.*?\.jpg)(\")(\/>)"
    
    # 编译匹配img标签的正则表达式               
    IMG_PATTERN_COMPILED = re.compile(IMG_PATTERN)
        
    # 匹配url中最长'/'字符的位置
    URL_PATTERN = ".*\/"
    
    # 编译匹配url中最长'/'的正则表达式
    URL_PATTERN_COMPILED = re.compile(URL_PATTERN)
    
    def __init__(self, book_url, book_name):
        
        # 电子书首页地址和电子书名称
        self.book_url = book_url
        self.book_name = book_name
    
    # 进行时间统计的装饰器函数
    def decorator(func):
        def wrapper(*args, **kwargs):
            print "*** Function Name:***",func.__name__
            #print "*** Function Args:***",args
            #print "*** Function kwargs:***",kwargs
            t1 = datetime.datetime.now()
            res = func(*args, **kwargs)
            t2 = datetime.datetime.now()
            print "*** Function Takes:***", (t2-t1), "Time"
            return res
        return wrapper
    
    def parse_url(self,url):
    
        '''
        根据每个章节的url地址，截取去掉index.html后的前缀
        '''
        
        match = re.match(self.URL_PATTERN_COMPILED,url)
        if match:
            return match.group(0)
        else:
            return None

    def get_total_chapter_urls(self):
        '''
        从电子书首页网址里，解析出全部章节的url地址，返回汇总列表
        '''
        
        resp = self.SESSION.get(self.book_url)
        soup = BeautifulSoup(resp.content,'html.parser')
        menu_tag = soup.find_all('ul',class_='summary')[0]
            
        url_total = []
        for li in menu_tag.find_all('li',class_='chapter'):
            url = self.BASE_URL + li.a.get('href')
            url_total.append(url)
        
        print "AAA url_total:",url_total
        return url_total
    
    def gen_book_html(self, chapter_name, chapter_url):
        '''
        爬取每一章电子书的url地址，生成每个章节对应的html页面.
        将img标签中的图片相对路径，使用正则表达式进行匹配后，使用re.sub函数将相对路径转换为绝对路径
        '''
        
        def gen_absolute_url(match):
            '''
            re.sub函数接收一个match对象作为参数
            gen_absolute_url函数用于拼接图片绝对路径的url网址
            '''
            rtn = ''.join([match.group(1), 
                           self.parse_url(chapter_url), 
                           match.group(2), 
                           match.group(3), 
                           match.group(4)])
            return str(rtn)
        
        resp = self.SESSION.get(chapter_url)
        soup = BeautifulSoup(resp.content,"html.parser")
        body = soup.find_all('div',class_='normal')[0]
        html_before = str(body)
            
        # 注:re.sub函数需要接收一个match对象作为参数
        html_after = re.sub(self.IMG_PATTERN_COMPILED, gen_absolute_url, html_before)
        
        html = self.HTML_TEMPLATE.format(content=html_after)
        
        with open(chapter_name,'wb') as fp:
            fp.write(html)
        
    @decorator
    def transfer_html_2_pdf(self, htmls, bookname):
        '''
        把所有html文件转换成pdf文件
        参数配置查看https://wkhtmltopdf.org/usage/wkhtmltopdf.txt
        '''
        
        options = {
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'minimum-font-size': 75,
                'zoom': 4,
                }
        print "*** Transfer_html_2_pdf begin ***"
        config = pdfkit.configuration(wkhtmltopdf='/usr/local/bin/wkhtmltopdf')
        pdfname = str(bookname) + '.pdf'
        pdfkit.from_file(htmls, pdfname, options=options, configuration=config)
        print "*** Transfer_html_2_pdf end ***"
    
    @decorator
    def run(self):
        
        print "*** PGM begin ***"
        # 打开SESSION连接
        self.login_with_session()
        
        chapter_name_tot = []
        
        for chapter_index, chapter_url in enumerate(self.get_total_chapter_urls()):
            chapter_name = ".".join([str(self.book_name), str(chapter_index), 'html'])
            chapter_name_tot.append(chapter_name)
            print "MAIN chapter_index:",chapter_index
            print "MAIN chapter_url:",chapter_url
            print "MAIN chapter_name:",chapter_name
            self.gen_book_html(chapter_name, chapter_url)
        
        # 将全部章节的html文件，合并生成一个pdf文件
        self.transfer_html_2_pdf(chapter_name_tot, self.book_name)
        
        # 关闭SESSION连接
        self.logoff_with_session()
        print "*** PGM end ***"
    
if __name__ == '__main__':

    bookindexurl = 'http://laidu.co/books/7fa8fcfa612989251007dafde19a1e86/index.html'
    bookname = '把时间当作朋友'
    p = Parse(bookindexurl,bookname)
    p.run()

    # 使用profile进行性能分析
    #profile.run('p.run()')
