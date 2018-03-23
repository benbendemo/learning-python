使用Python爬虫下载电子书
======================

这两天将半年前写的爬虫代码重构了一下，本来以为要不了多久，结果前前后后花了我将近4个小时的时间。无力吐槽！半年前的代码是一个面向过程的处理，几个函数顺序执行，最终慢悠悠地把PDF生成出来，功能都齐全，但是可读性和拓展性极差。现在全部改为面向对象处理，将requests.Session操作剥离出来作为Crawler类，将解析网页的操作剥离出来作为Parse类，结构清楚了很多，耦合度（较之前）大大降低，基本达到我的要求。

整体功能实现后，我写了一个cache函数，将Session操作缓存起来方便后续调用，本地调试成功，但最终没有采用，因为我设想的是将Session常驻内存，每次执行前检查缓存中有没有，有的话就直接用，没有才新建。但我这个cache函数是程序执行完后缓存的内容直接被释放。这几天在学习redis，估计我想要的效果得用redis才能实现。

在将网页生成HTML文件到本地后，使用pdfkit工具将HTML文件转换为PDF很耗费时间，这一点请大家注意。

#### 环境准备

Mac os 10.11.6 + Anaconda Navigator 1.7.0+ Python 2.7.12 + Sublime 3.0

#### 技术要点

- Requests会话处理
- BeautifulSoup网页解析技巧
- pdfkit工具（注意，一定要先安装wkhtmltopdf这个工具包）
- decorator装饰器

<!--more-->

#### 代码实现

```python
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
        # 这里需要先注册来读，然后把邮箱和密码换成你自己的
        payload = {
                   'email': 'XXXXXXXX', 
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
```

#### 执行结果

- 生成的HTML文件和最终PDF文件如下。

  ![htmls and pdf](https://github.com/benbendemo/learning-python/blob/master/python-crawler/htmls_and_pdf.jpg)

  ​


- 生成PDF文件预览，注意红色方框第5章第4节"逆命题"出现错位，我检查过，不是网页解析的问题，是电子书HTML文件源码中"逆命题"那一节的文本标签被错误定义为"h1"，手工将文件改为"h2"，再生成PDF就能修复这个问题。

  ![pdf snapchat](https://github.com/benbendemo/learning-python/blob/master/python-crawler/pdf_snapchat.jpg)

  ​

- 输出的LOG如下。

  ```shell
  runfile('/Users/jacksonshawn/PythonCodes/pythonlearning/python_learning_crawler_laidu_new.py', wdir='/Users/jacksonshawn/PythonCodes/pythonlearning')
  *** Function Name:*** run
  *** PGM begin ***
  ---xsrf---: f8EMOPQer81CI4xwn3mQ8ccqnyLikVRNQAMk5887
  MAIN chapter_index: 0
  MAIN chapter_url: http://laidu.co/books/7fa8fcfa612989251007dafde19a1e86/index.html
  MAIN chapter_name: 把时间当做朋友.0.html
  MAIN chapter_index: 1
  MAIN chapter_url: http://laidu.co/books/7fa8fcfa612989251007dafde19a1e86/Preface.html
  MAIN chapter_name: 把时间当做朋友.1.html
  MAIN chapter_index: 2
  MAIN chapter_url: http://laidu.co/books/7fa8fcfa612989251007dafde19a1e86/Forword.html
  MAIN chapter_name: 把时间当做朋友.2.html
  MAIN chapter_index: 3
  MAIN chapter_url: http://laidu.co/books/7fa8fcfa612989251007dafde19a1e86/Chapter0.html
  MAIN chapter_name: 把时间当做朋友.3.html
  MAIN chapter_index: 4
  MAIN chapter_url: http://laidu.co/books/7fa8fcfa612989251007dafde19a1e86/Chapter1.html
  MAIN chapter_name: 把时间当做朋友.4.html
  MAIN chapter_index: 5
  MAIN chapter_url: http://laidu.co/books/7fa8fcfa612989251007dafde19a1e86/Chapter2.html
  MAIN chapter_name: 把时间当做朋友.5.html
  MAIN chapter_index: 6
  MAIN chapter_url: http://laidu.co/books/7fa8fcfa612989251007dafde19a1e86/Chapter3.html
  MAIN chapter_name: 把时间当做朋友.6.html
  MAIN chapter_index: 7
  MAIN chapter_url: http://laidu.co/books/7fa8fcfa612989251007dafde19a1e86/Chapter4.html
  MAIN chapter_name: 把时间当做朋友.7.html
  MAIN chapter_index: 8
  MAIN chapter_url: http://laidu.co/books/7fa8fcfa612989251007dafde19a1e86/Chapter5.html
  MAIN chapter_name: 把时间当做朋友.8.html
  MAIN chapter_index: 9
  MAIN chapter_url: http://laidu.co/books/7fa8fcfa612989251007dafde19a1e86/Chapter6.html
  MAIN chapter_name: 把时间当做朋友.9.html
  MAIN chapter_index: 10
  MAIN chapter_url: http://laidu.co/books/7fa8fcfa612989251007dafde19a1e86/Chapter7.html
  MAIN chapter_name: 把时间当做朋友.10.html
  *** Function Name:*** transfer_html_2_pdf
  *** Transfer_html_2_pdf begin ***
  Loading pages (1/6)
  libpng warning: iCCP: known incorrect sRGB profile           ] 50%
  libpng warning: iCCP: known incorrect sRGB profile           ] 52%
  libpng warning: iCCP: known incorrect sRGB profile           ] 52%
  libpng warning: iCCP: known incorrect sRGB profile           ] 56%
  libpng warning: iCCP: known incorrect sRGB profile           ] 56%
  libpng warning: iCCP: known incorrect sRGB profile           ] 56%
  libpng warning: iCCP: known incorrect sRGB profile           ] 59%
  libpng warning: iCCP: known incorrect sRGB profile           ] 60%
  libpng warning: iCCP: known incorrect sRGB profile           ] 60%
  libpng warning: iCCP: known incorrect sRGB profile           ] 61%
  libpng warning: iCCP: known incorrect sRGB profile           ] 62%
  libpng warning: iCCP: known incorrect sRGB profile           ] 63%
  libpng warning: iCCP: known incorrect sRGB profile           ] 64%
  libpng warning: iCCP: known incorrect sRGB profile           ] 64%
  libpng warning: iCCP: known incorrect sRGB profile           ] 64%
  libpng warning: iCCP: known incorrect sRGB profile           ] 64%
  libpng warning: iCCP: known incorrect sRGB profile           ] 66%
  libpng warning: iCCP: known incorrect sRGB profile           ] 68%
  libpng warning: iCCP: known incorrect sRGB profile           ] 69%
  libpng warning: iCCP: known incorrect sRGB profile           ] 69%
  libpng warning: iCCP: known incorrect sRGB profile           ] 70%
  libpng warning: iCCP: known incorrect sRGB profile           ] 71%
  libpng warning: iCCP: known incorrect sRGB profile           ] 71%
  libpng warning: iCCP: known incorrect sRGB profile           ] 71%
  libpng warning: iCCP: known incorrect sRGB profile           ] 72%
  libpng warning: iCCP: known incorrect sRGB profile           ] 72%
  libpng warning: iCCP: known incorrect sRGB profile           ] 73%
  libpng warning: iCCP: known incorrect sRGB profile           ] 73%
  libpng warning: iCCP: known incorrect sRGB profile
  libpng warning: iCCP: known incorrect sRGB profile           ] 76%
  libpng warning: iCCP: known incorrect sRGB profile           ] 78%
  libpng warning: iCCP: known incorrect sRGB profile           ] 80%
  libpng warning: iCCP: known incorrect sRGB profile=>         ] 84%
  libpng warning: iCCP: known incorrect sRGB profile===>       ] 88%
  libpng warning: iCCP: known incorrect sRGB profile====>      ] 89%
  libpng warning: iCCP: known incorrect sRGB profile=====>     ] 90%
  libpng warning: iCCP: known incorrect sRGB profile=====>     ] 91%
  libpng warning: iCCP: known incorrect sRGB profile======>    ] 93%
  libpng warning: iCCP: known incorrect sRGB profile========>  ] 95%
  libpng warning: iCCP: known incorrect sRGB profile========>  ] 96%
  libpng warning: iCCP: known incorrect sRGB profile==========>] 99%
  Counting pages (2/6)                                               
  Resolving links (4/6)                                                         
  Loading headers and footers (5/6)                                             
  Printing pages (6/6)
  Done                                                                          
  *** Transfer_html_2_pdf end ***
  *** Function Takes:*** 0:01:09.791587 Time
  *** PGM end ***
  *** Function Takes:*** 0:01:16.134701 Time
  ```


#### 总结

1. 使用pdfkit生成PDF文件，必须要先安装[wkhtmltopdf](https://wkhtmltopdf.org/downloads.html)这个工具。pdfkit只是一个入口程序，真正生成PDF这些脏活累活，都是wkhtmltopdf完成的。安装wkhtmltopdf成功后，在transfer_html_2_pdf函数中一定要指定正确的调用路径。

2. 目前还没有设置缓存机制，这两天在看Redis，打算后续会加一个缓存处理。

3. Crawler类里面使用的@classmethod装饰器，其实完全可以拿掉不要，我测试过，不用@classmtehod也没问题。

4. Parse类里面用到的decorator装饰器，其实可以剥离出来成为一个单独的类，进一步降低耦合度。

5. 可以使用profile.run('p.run()')跑性能检测作业。目前最耗费时间的操作在生成PDF文件那一步，爬取网页操作其实要不了多少时间。

**原文链接：**

- [使用Python爬虫下载电子书](http://bigbigben.com/2018/03/21/python-crawler/)

**参考资料：**

- [PDFKIT参数说明](https://wkhtmltopdf.org/usage/wkhtmltopdf.txt)
