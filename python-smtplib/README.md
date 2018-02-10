Python+MySqldb+Pandas+Smtplib发送邮件
====================================

今天看到又耳笔记这篇[**导出mysql数据，利用pandas生成excel文档，并发送邮件**](http://blog.51cto.com/youerning/1708941)"Pandas获取数据，smtplib发送邮件"文章时，我决定把它实现出来。

查资料、编码、测试、优化、写注释......花了3个多小时将全部工作完成。本文贴出的就是全部代码，只要安装了对应的包，在Python 2.7环境下可以直接拿过去跑，本机测试邮件能够发送成功。没有Mysql和Pandas也不要紧，跳过fetch_db和gen_xls函数，直接执行sendmsg就行。

目前在正则表达式匹配邮箱地址那一环节还存有缺陷，日后有待完善，欢迎移步关注我的github帐号。

环境准备：
-------
Mac os 10.11.6 + Anaconda Navigator 1.2.1+ Python 2.7.12 + Sublime 3.0

技术要点：
-------
- Mysqldb数据库连接
- Pandas dataframe转换Excel文件
- 正则表达式匹配邮箱
- smtplib协议

代码实现：
-------
https://github.com/benbendemo/learning-python/blob/master/python-smtplib/python_learning_send_email.py

执行结果：
-------
生成的excel文件如下图所示，表中数据使用tushare获取。
![allAstockinfo Table](https://github.com/benbendemo/learning-python/blob/master/python-smtplib/allAstockInfo_table.jpg)

登录邮箱，显示邮件发送成功，附件内容与excel数据一致，没有乱码。
![Email screenshot](https://github.com/benbendemo/learning-python/blob/master/python-smtplib/163_email_screen_snapchat.jpg)

总结：
----
全部代码150多行，没有什么复杂的技术难题，对老司机来说，这个任务小菜一碟。如果没有Python基础，有些地方可能需要花一些时间理解。亲自动手写一遍之后，才对SMTP协议有比较深入的理解。

**参考资料：**
- [SMTP发送邮件](https://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000/001386832745198026a685614e7462fb57dbf733cc9f3ad000)
- [Zabbix监控之邮件发送失败-smtp-server: 错误代码550与535](http://blog.51cto.com/clovemfong/1702105)

**延伸阅读：**
- [MIME笔记](http://www.ruanyifeng.com/blog/2008/06/mime.html)
- [如何验证 Email 地址：SMTP 协议入门教程](http://www.ruanyifeng.com/blog/2017/06/smtp-protocol.html)
- [Base64笔记](http://www.ruanyifeng.com/blog/2008/06/base64.html)

**原文链接: **
