通过月平息计算实际年利率
======================

很多金融机构发放贷款都以"月平息低至多少多少"作为卖点来吸引顾客，如果要知道这笔贷款的实际利率是多少，就需要转化为实际年利率(APR)进行计算比较。

比如，贷款20W，年平息2.5%（对应月平息就是2.5%/12=0.2083%），期限24个月，计算出贷款总利息为10,000，每月供款金额为8750.00，那么它的实际年利率
是多少呢？

中银香港提供了一种计算方法，但它有一个问题，它的月平息利率最多只能输入3位小数，算出来的值不够准确。
![boc HK](https://github.com/benbendemo/learning-python/blob/master/python-apr/boc_hk_flat_2_apr.jpg)


此外，如果月平息利率想输入四位小数计算得更精确一些，如下图输入0.2083，它会直接提示报错。
![boc HK error](https://github.com/benbendemo/learning-python/blob/master/python-apr/boc_hk_flat_2_apr_error.jpg)

可能这个网站一般人都不会去用吧，他们也就不去更新维护了，但作为金融领域专业人士的我（“咳咳”，有点吹牛逼了，请允许我往自己脸上贴这个金。），是无法
容忍这个结果的。要知道，小数精确位数不够，在金融领域实际计算出来的误差可以大到吓人啊。

我们得另谋它法。

<!--more-->

在CCBA项目中，我们经常要对一笔Addon贷款进行实际年利率的计算，最开始就是用的这种方法，发现它计算出来的结果并不准确后，我们用了行方提供
的一个Excel计算工具才得以解决问题。我们借鉴那个工具里面的Excel Rate函数来进行计算。


方法一：使用Excel Rate函数进行计算APR。
-----------------------------------

*Step1* - 根据年平息计算出每月供款额
(20W+200,000*2.5%*2)/24=8750

*Step2* - 根据等额本息月供款额计算公式，计算每个月的月利率
200,000*X*(1+X)^{24}/[(1+X)^{24}-1]=8750

这是一个一元24次方程，它并没有一个固定的求根公式。你是无法通过解方程算X的值的。怎么办啊？Excel里面的Rate函数可以帮上忙。
![Excel Rate function](https://github.com/benbendemo/learning-python/blob/master/python-apr/excel-rate-function.jpg)

*Step3* - 将每个月的月利率（单元格B4）乘以12就可以得到实际年利率APR
APR=0.00394060*12=0.04728721

方法二：写一个Python程序来计算APR。（我发现Python语言干这种事情非常轻巧、方便。）
--------------------------------------------------------------------------

代码实现：
-------
https://github.com/benbendemo/learning-python/blob/master/python-apr/python-flatrate-2-apr.py


计算结果：
--------
MPR is: 0.00394058999998
Max_MPR is: 0.04375
APR is: 0.0472870799998
[Finished in 0.4s]


需要注意的是，这里计算得出的数值0.0472870799998，它是一个近似值，并不是精确值，是一个误差被我控制在0.00000001之内的结果。你可以认为
方法一里面Excel Rate函数计算出来的0.04728721是精确值。与其相比，Python程序计算出来的0.0472870799998，与精确值非常接近，可以将其当
作精确值使用。

原文链接:
-------
https://bigbigben.com/2018/12/15/monthly-flat-rate/


**参考资料:**
- [月平息兑换实际年利率](https://www.bochk.com/sc/home/calculators/flatratevsapr.html)

- [Excel RATE 函数](https://support.office.com/zh-cn/article/rate-函数-9f665657-4a7e-4bb7-a030-83fc59e748ce)
