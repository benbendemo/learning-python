# -*- coding: utf-8 -*-
"""
Created on Sat Jul 07 17:28:45 2019
PGM:python_learning_spzj_publishcp_bytesio.py
fun:使用selenium登录网站并实现自动发布票据
@author: jacksonshawn
"""
import os
import sys
import re
import time
import random
import datetime
from faker import Faker
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aip import AipOcr

if sys.version_info > (3, 0):
    python_version3_flag = 'Y'
    import base64
    from io import BytesIO
else:
    python_version3_flag = 'N'
    try:
        import cStringIO as StringIO
    except ImportError:
        import StringIO

# 百度OCR应用apikey
BD_OCR_APPNAME = 'XXXXXXXX'
BD_OCR_APPID = 'XXXXXXXX'
BD_OCR_APIKEY = 'XXXXXXXX'
BD_OCR_SECRETKEY = 'XXXXXXXX'

# AutoIt程序(使用两个exe文件所在路径)
AI32_EXE = "ai_uploadpic32.exe"
AI64_EXE = "ai_uploadpic64.exe"

# 票据正反面图片(指定要上传的图片)
CP_FRONT_IMG = "XXXXXXXX"
CP_BACK_IMG = "XXXXXXXX"

# 初始化登录Flag
LOGIN_SUCCESS_FLAG = 'N'
LOGIN_USERNAME = 'XXXXXXXX'
LOGIN_PASSWORD = 'XXXXXXXX'
LOGIN_URL = 'XXXXXXXX'


def autoit_upload(cp_pic,
                  exe_path_32=AI32_EXE,
                  exe_path_64=AI64_EXE):

    cmd_path = ''
    if sys.platform == 'win32':
        cmd_path = exe_path_32 + " " + cp_pic
    elif sys.platform == 'win64':
        cmd_path = exe_path_64 + " " + cp_pic
    exec_result = os.system(cmd_path)
    print ("autoit_upload exec_result:", exec_result)
    # ps=subprocess.Popen(cmd)
    # ps.wait()


class CPData(object):

    UnifiedSocialCreditCode_1_2_list = [
                        '11',
                        '12',
                        '13',
                        '19',
                        '51',
                        '52',
                        '53',
                        '59',
                        '91',
                        '92',
                        '93',
                        'Y1']

    areaDataDict_list = {
                        '232722': '黑龙江省大兴安岭地区塔河县', '232723': '黑龙江省大兴安岭地区漠河县',
                        '342531': '安徽省宣城地区绩溪县', '430304': '湖南省湘潭市岳塘区',
                        '342530': '安徽省宣城地区旌德县', '360281': '江西省景德镇市乐平市',
                        '622600': '甘肃省陇南地区', '510108': '四川省成都市成华区',
                        '421087': '湖北省荆州市松滋市', '542424': '西藏自治区那曲地区聂荣县',
                        '441502': '广东省汕尾市城区', '440684': '广东省佛山市高明市',
                        '652925': '新疆维吾尔族自治区阿克苏地区新和县', '440823': '广东省湛江市遂溪县',
                        '632124': '青海省海东地区湟中县', '542427': '西藏自治区那曲地区索县',
                        '441423': '广东省梅州市丰顺县', '440825': '广东省湛江市徐闻县',
                        '342623': '安徽省巢湖地区无为县', '370826': '山东省济宁市微山县',
                        '441422': '广东省梅州市大埔县', '441421': '广东省梅州市梅县',
                        '441427': '广东省梅州市蕉岭县', '441426': '广东省梅州市平远县',
                        '620102': '甘肃省兰州市城关区', '441424': '广东省梅州市五华县',
                        '230381': '黑龙江省鸡西市虎林市', '652926': '新疆维吾尔族自治区阿克苏地区拜城县',
                        '370103': '山东省济南市市中区', '342626': '安徽省巢湖地区和县',
                        '230382': '黑龙江省鸡西市密山市', '342625': '安徽省巢湖地区含山县',
                        '342622': '安徽省巢湖地区庐江县', '370101': '山东省济南市市辖区', '370100': '山东省济南市'}

    bank_list = {
                '104584000003': '中国银行深圳市分行',
                '104584001022': '中国银行深圳国贸支行',
                '104584001039': '中国银行深圳罗湖支行',
                '104584001047': '中国银行深圳东门支行'}

    fake = Faker("zh_CN")

    def __init__(self):
        '''
        对变量进行初始化赋值
        '''
        self.fake_name = self.fake.name()
        self.fake_province = self.fake.province()
        self.fake_city = self.fake.city()
        self.fake_company = self.fake_province + self.fake.company()
        self.fake_company_email = self.fake.company_email()
        self.fake_bankcard_no = '62' + self.fake.credit_card_number()
        self.fake_phone_no = self.fake.phone_number()
        self.fake_ssn_no = self.fake.ssn()
        self.fake_address = self.fake.address()

    @staticmethod
    def gen_fake_data():

        fake = Faker("zh_CN")
        fake_name = fake.name()
        fake_province = fake.province()
        fake_city = fake.city()
        fake_company = fake_province+fake.company()
        fake_company_email = fake.company_email()
        fake_bankcard_no = '62'+fake.credit_card_number()
        fake_phone_no = fake.phone_number()
        fake_ssn_no = fake.ssn()
        fake_address = fake.address()
        print ("BBB Fake姓名:", fake_name)
        print ("BBB Fake省份:", fake_province)
        print ("BBB Fake城市:", fake_city)
        print ("BBB Fake公司名称:", fake_company)
        print ("BBB Fake公司邮箱:", fake_company_email)
        print ("BBB Fake银行卡号:", fake_bankcard_no)
        print ("BBB Fake手机号:", fake_phone_no)
        print ("BBB Fake身份证:", fake_ssn_no)
        print ("BBB Fake地址:", fake_address)

    @staticmethod
    def genAreaCodeDict(fileName):

        areaDataDict = {}
        key = 0
        value = 1
        # dataLine=open(fileName,encoding="utf-8").read().splitlines()
        with open(fileName) as fp:
            dataLine = fp.read().splitlines()
            for line in dataLine:
                tempList = line.split(",")
                areaDataDict[tempList[key]] = tempList[value]

        areaDataDict_printable = repr(areaDataDict).decode('string_escape')

        print ("areaDataDict:", areaDataDict_printable)
        return areaDataDict

    # 功能：随机生成一个区域码
    @staticmethod
    def genRandomAreaCode(areaDataDict):

        areaCodeList = []
        for key in areaDataDict.keys():
            areaCodeList.append(key)
        lenth = len(areaCodeList)-1
        i = random.randint(0, lenth)
        return areaCodeList[i]

    @classmethod
    def genUnifiedSocialCreditCode_1_2(cls):

        '''
        生成统一信仰机构代码前2位
        '''
        UnifiedSocialCreditCode_1_2 = random.choice(cls.UnifiedSocialCreditCode_1_2_list)
        print ("UnifiedSocialCreditCode_1_2:", UnifiedSocialCreditCode_1_2)
        return UnifiedSocialCreditCode_1_2

    @classmethod
    def genUnifiedSocialCreditCode_3_8(cls):

        '''
        生成统一信仰机构代码第3位到第8位
        '''
        # UnifiedSocialCreditCode_3_8 = cls.genRandomAreaCode(cls.genAreaCodeDict(fileName))
        UnifiedSocialCreditCode_3_8 = cls.genRandomAreaCode(cls.areaDataDict_list)
        print ("UnifiedSocialCreditCode_3_8:", UnifiedSocialCreditCode_3_8)
        return UnifiedSocialCreditCode_3_8

    @staticmethod
    def gen_orgcode_usccode():

        '''
        生成统一信仰机构代码第9位到第17位以及加上最后一位校验位
        '''
        # 组织机构代码本体代码加权因子数值从左到右分别是：3、7、9、10、5、8、4、2
        ww = [3, 7, 9, 10, 5, 8, 4, 2]
        cc = []
        dd = 0

        for i in range(8):
            cc.append(random.randint(1, 9))
            dd = dd+cc[i]*ww[i]
        for i in range(len(cc)):
            cc[i] = str(cc[i])
        C9 = 11-dd % 11
        if C9 == 10:
            C9 = 'X'
        else:
            if C9 == 11:
                C9 = '0'
            else:
                C9 = str(C9)
        cc.append(C9)
        companyOrgCode = "".join(cc)
        print ("CCC 组织机构代码:", companyOrgCode)
        return companyOrgCode

    @classmethod
    def gen_uscc_chkcode(cls):

        '''
        生成统一信仰机构代码最后一位校验位
        '''
        UnifiedSocialCreditCode_1_2 = cls.genUnifiedSocialCreditCode_1_2()
        UnifiedSocialCreditCode_3_8 = cls.genUnifiedSocialCreditCode_3_8()
        UnifiedSocialCreditCode_9_17 = cls.gen_orgcode_usccode()
        UnifiedSocialCreditCode_1_17 = str(UnifiedSocialCreditCode_1_2) + \
                                       str(UnifiedSocialCreditCode_3_8) + \
                                       str(UnifiedSocialCreditCode_9_17)

        # 统一信用代码中'组织机构号码'字母映射关系
        dict_org_code = {'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14,
                         'F': 15, 'G': 16, 'H': 17, 'J': 18, 'K': 19,
                         'L': 20, 'M': 21, 'N': 22, 'P': 23, 'Q': 24,
                         'R': 25, 'T': 26, 'U': 27, 'W': 28, 'X': 29, 'Y': 30}
        # 统一信用机构代码加权因子数值从左到右分别是：
        # 1、3、9、27、19、26、16、17、20、29、25、13、8、24、10、30、2​8
        ww = [1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28]
        dd = 0

        for i in range(17):
            if UnifiedSocialCreditCode_1_17[i] in dict_org_code:
                dd = dd + dict_org_code.get(UnifiedSocialCreditCode_1_17[i]) * ww[i]
            else:
                dd = dd + int(UnifiedSocialCreditCode_1_17[i]) * ww[i]

        C18 = 31-dd % 31
        dict_org_code_reverse = {v: k for k, v in dict_org_code.items()}

        if C18 <= 9:
            C18 = str(C18)
        else:
            if C18 in dict_org_code_reverse:
                C18 = dict_org_code_reverse.get(C18)

        UnifiedSocialCreditCode_1_18 = UnifiedSocialCreditCode_1_17 + str(C18)
        print ("EEE 统一社会信用代码:", UnifiedSocialCreditCode_1_18)

    @classmethod
    def gen_bill_no(cls):
        '''
        电子商业汇票的“电子票据号码”分为5个部分，共30位，全部由阿拉伯数字组成，具体结构如下
        a:票据种类(1位数字,1表示银票,2表示商票)
        b:支付系统行号(12位数字,各支付银行行号)
        c:出票登记日期(8位日期值,YYYYMMDD)
        d:ECDS当天唯一流水号(8位数字)
        e:ECDS校验码(1位数字,校验规则未知)
        '''

        bill_dict = {1: '银票', 2: '商票'}
        bill_pay_bankno_list = [
                    102100000021,
                    102100000030,
                    102100000048,
                    102100000056,
                    102100000064,
                    102100000072,
                    102100000089,
                    102100000097,
                    102100000101,
                    102100000110]

        bill_type = str(2)
        bill_pay_bankno = str(random.choice(bill_pay_bankno_list))
        date = datetime.date.today().strftime('%Y%m%d')
        ecds_jrnno = str(random.randint(10000000, 99999999))  # 随机生成8位数字
        ecds_chkcode = str(random.randint(1, 9))  # 随机生成1位校验码

        bill_no = ''.join([bill_type,
                           bill_pay_bankno,
                           date,
                           ecds_jrnno,
                           ecds_chkcode])

        print ("DDD 票据号码:", bill_no)
        return bill_no

    # 功能：随机生成1930年之后的出生日期
    @staticmethod
    def genBirthDay():
        d1 = datetime.datetime.strptime('1930-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        d2 = datetime.datetime.now()
        delta = d2-d1
        dys = delta.days
        i = random.randint(0, dys)
        dta = datetime.timedelta(days=i)
        birthday = d1+dta
        return birthday.strftime('%Y%m%d')

    # 功能：随机生成身份证里的3位序列号和身份证号性别
    @staticmethod
    def genRandomSeqNum():
        randomSeqNum = random.randint(100, 999)  # 随机生成100到999之间的3为数据
        randomSex = randomSeqNum % 2
        return (str(randomSeqNum), randomSex)

    # 功能：生成身份证最后一位校验码
    @staticmethod
    def genCheckCode(id_num):
        i = 0
        count = 0
        weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]  # 权重项
        checkcode = {'0': '1', '1': '0', '2': 'X', '3': '9', '4': '8',
                     '5': '7', '6': '6', '7': '5', '8': '5', '9': '3',
                     '10': '2'}  # 校验码映射
        for i in range(0, len(id_num)):
            count = count + int(id_num[i])*weight[i]
        return checkcode[str(count % 11)]  # 算出校验码

    # 功能：生成身份证号，返回地区代码
    @classmethod
    def gen_idcard(cls):

        randomBirthDay = cls.genBirthDay()   # 生成出生日期
        (randomSeqNum, randomSex) = cls.genRandomSeqNum()   # 生成顺序号和性别
        # 生产校验码
        checkcode = cls.genCheckCode((cls.genUnifiedSocialCreditCode_3_8() +
                                  randomBirthDay +
                                  randomSeqNum))
        # 拼装身份证号
        randomIdCard = cls.genUnifiedSocialCreditCode_3_8() + \
                       randomBirthDay + \
                       randomSeqNum + \
                       checkcode
        print ("AAA 身份证号(通过校验):", randomIdCard)


def baiduocr_img2text(image_flow):

    """ 调用通用文字识别（高精度版） """
    try:
        aipocr_client = AipOcr(BD_OCR_APPID,
                               BD_OCR_APIKEY,
                               BD_OCR_SECRETKEY)
    except Exception as e:
        print ("BD_OCR Error AAA:\n", type(e), e)
        return 'ERRORCODE'
    else:
        """ 如果有可选参数 """
        options = {}
        options["language_type"] = "CHN_ENG"
        options["detect_direction"] = "true"
        options["detect_language"] = "true"
        options["probability"] = "true"

        """ 带参数调用通用文字识别, 图片参数为本地图片 """
        try:
            result = aipocr_client.basicAccurate(image_flow, options)
        except Exception as e:
            print ("BD_OCR Error BBB:\n", type(e), e)
            return 'ERRORCODE'
        else:
            if result is None:
                return 'ERRORCODE'
            else:
                if 'words_result' in result.keys():
                    list_words_result = result['words_result']
                else:
                    return 'ERRORCODE'

            for x in list_words_result:
                print ("BD_OCR ImageText:", x['words'].replace(' ', ''))
                # 替换识别字符中的空格
                if x['words'].replace(' ', ''):
                    return x['words'].replace(' ', '')
                else:
                    # 如果百度OCR识别结果不是None，正常返回
                    return 'ERRORCODE'


class BrowserDriver(object):

    url = LOGIN_URL
    username = LOGIN_USERNAME
    password = LOGIN_PASSWORD
    verifycode = ''

    # prefs = { 'profile.default_content_setting_values': {'javascript': 2, } }

    def __init__(self):

        self.newdriver = None
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('disable-infobars')
        # self.options.add_experimental_option("prefs", self.prefs)
        self.driver = webdriver.Chrome(chrome_options=self.options)
        self.driver.maximize_window()
        self.driver.get(self.url)

    def browser_quit(self):

        time.sleep(random.randint(5, 10))
        self.driver.quit()

    @staticmethod
    def base64_to_image(base64_str, IMAGE_FLOW):

        base64_str1 = base64_str.split(',')[1]
        base64_str2 = re.sub(r'%0A', "\\n", base64_str1)
        # print ("base64_str2:", base64_str2)

        if sys.version_info > (3, 0):
            # IMAGE_FLOW = BytesIO()
            base64_str3 = base64.b64decode(base64_str2.encode('utf-8'))
            # print ("AAA base64_str3:", base64_str3)
            # IMAGE_FLOW.truncate(0)
            IMAGE_FLOW.write(base64_str3)
            # print ("base64_to_image IMAGE_FLOW getvalue:",IMAGE_FLOW.getvalue())
        else:
            # IMAGE_FLOW = StringIO.StringIO()
            base64_str3 = base64_str2.decode('base64')
            # IMAGE_FLOW.truncate(0)
            IMAGE_FLOW.write(base64_str3)

    def get_chkcode_image(self, login_time, image_flow):

        print ("get_chkcode_image login_time:", login_time)
        try:
            # 定位登录Button
            if login_time == 0:
                self.browser_webdriverwait_by_clickable(By.CSS_SELECTOR, ".fl.captcha-img")
                # WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".fl.captcha-img")))
            else:
                pass
        except Exception as e:
            print ("Exception get_chkcode_image type:", type(e))
            print ("Exception get_chkcode_image value:", e)
        else:
            ele_text = self.browser_find_element_by_css_selector(".fl.captcha-img").get_attribute('src')
            self.base64_to_image(ele_text, image_flow)

    def browser_webdriverwait_by_clickable(self, method, ele_name, time=10):

        WebDriverWait(self.driver, time).until(EC.element_to_be_clickable((method, ele_name)))

    def browser_find_element_by_id(self, ele_name):

        time.sleep(random.randint(1, 3))
        return self.driver.find_element_by_id(ele_name)

    def browser_find_element_by_class_name(self, ele_name):

        time.sleep(random.randint(1, 3))
        return self.driver.find_element_by_class_name(ele_name)

    def browser_find_element_by_name(self, ele_name):

        time.sleep(random.randint(1, 3))
        return self.driver.find_element_by_name(ele_name)

    def browser_find_element_by_css_selector(self, ele_name):

        time.sleep(random.randint(1, 3))
        return self.driver.find_element_by_css_selector(ele_name)

    def browser_find_elements_by_tag_name(self, ele_name):

        time.sleep(random.randint(1, 3))
        return self.driver.find_elements_by_tag_name(ele_name)

    def browser_switch_window(self):

        current_handle = self.driver.current_window_handle
        all_handles = self.driver.window_handles
        new_window_inform = 'No new window!'

        for h in all_handles:
            if h != current_handle:
                self.newdriver = self.driver.switch_to.window(h)
                new_window_inform = 'New window open'
                break

        return new_window_inform

    def browser_login(self, login_time):

        global LOGIN_SUCCESS_FLAG

        if login_time == 0:
            try:
                # 第一次登录时取消百度商桥客服弹框
                self.browser_webdriverwait_by_clickable(By.ID, "nb_invite_cancel")
                # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "nb_invite_cancel")))
            except Exception as e:
                print ("Exception login1 type:", type(e))
                print ("Exception login1 value:", e)
            else:
                self.browser_find_element_by_id('nb_invite_cancel').click()

        try:
            self.browser_webdriverwait_by_clickable(By.ID, "loginBtn")
            # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "loginBtn")))
        except Exception as e:
            print ("Exception login2 type:", type(e))
            print ("Exception login2 value:", e)
        else:
            if login_time == 0:
                # 第一次登录时需要清除帐号和密码再上传数据
                self.browser_find_element_by_id('mcode').clear()
                self.browser_find_element_by_id('mcode').send_keys(self.username)

                self.browser_find_element_by_id('password').clear()
                self.browser_find_element_by_id('password').send_keys(self.password)
            else:
                pass

            self.browser_find_element_by_id('vcode0').clear()
            self.browser_find_element_by_id('vcode0').send_keys(self.verifycode)
            self.browser_find_element_by_id('loginBtn').click()

        try:
            # 登录时验证码或密码出错时获取弹框的Button ID
            self.browser_webdriverwait_by_clickable(By.CLASS_NAME, "layui-layer-btn0")
            # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "layui-layer-btn0")))
        except Exception as e:
            # 如果没有弹出密码或验证码弹框认为登录成功
            if type(e) == 'TimeoutException' or type(e) == 'selenium.common.exceptions.TimeoutException' \
                  or e == 'selenium.common.exceptions.TimeoutException' or e == 'TimeoutException':
                LOGIN_SUCCESS_FLAG = 'Y'
                print ("Login Successful")
            else:
                LOGIN_SUCCESS_FLAG = 'Y'
                print ("Login Successful without chk exception")
        else:

            layui_layer_btn0_text = self.browser_find_element_by_class_name('layui-layer-btn0').text
            if layui_layer_btn0_text == u'确认':
                self.browser_find_element_by_class_name('layui-layer-btn0').click()
            else:
                LOGIN_SUCCESS_FLAG = 'Y'

        return LOGIN_SUCCESS_FLAG

    def browser_login_success_chk(self):

        try:
            WebDriverWait(self.driver, 10).until(lambda driver: self.browser_find_element_by_id("currentRole").text)
        except Exception as e:
            print ("Exception login_success_chk type:", type(e))
            print ("Exception login_success_chk value:", e)
        else:
            currentRole_text = self.browser_find_element_by_id('currentRole').text
            userInfo_text = self.browser_find_element_by_id('userInfo').text
            print ("currentRole_text:", currentRole_text)
            print ("userInfo_text:", userInfo_text)

    def browser_refresh(self):

        self.driver.refresh()

    def browser_get_current_url(self):

        return self.driver.current_url

    def browser_choose_company(self):

        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((BY.ID, 'company_list_wrap')))
        except Exception as e:
            pass
        else:
            # ele_companyListWrap = self.driver.find_element_by_class_name('company-list-wrap')
            ele_companyList = self.browser_find_element_by_id('company_list_wrap').find_elements_by_class_name('company-item')
            ele_company = ele_companyList[0].click()

            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((BY.CLASS_NAME, 'globalData_comAuth_title')))
            except Exception as e:
                pass
            else:
                print ("browser_choose_company企业没有实名认证")

    def browser_page_back(self):

        self.driver.back()

    def browser_page_forward(self):

        self.driver.forward()

    def browser_move_to_publishpage(self):

        try:
            # 点击我要发布按钮,之前使用的id是gotoPublish
            self.browser_webdriverwait_by_clickable(By.ID, "navTabs")
            # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "navTabs")))
        except Exception as e:
            print ("Exception move_to_publish type:", type(e))
            print ("Exception move_to_publish value:", e)
        else:
            self.browser_find_element_by_id('navTabs').find_elements_by_css_selector('li')[2].click()

    def autoit_upload_cp_pic(self, ele_name, cp_pic):

        try:
            print ("upload_cp_pic begin")
            # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "layui-upload-img")))
            self.browser_webdriverwait_by_clickable(By.CLASS_NAME, ele_name)
        except Exception as e:
            print ("Exception upload_cp_pic BBB type:", type(e))
            print ("Exception upload_cp_pic BBB value:", e)
            self.browser_quit()
        else:
            self.browser_find_element_by_class_name(ele_name).click()
            autoit_upload(cp_pic)
            print ("upload_cp_pic finish")

    def browser_upload_cp_field(self, cpinfo):

        self.browser_find_element_by_name('acceptor').clear()
        self.browser_find_element_by_name('acceptor').send_keys(cpinfo.fake_company)

        self.browser_find_element_by_name('dueDate').click()
        ele_date_ele = self.browser_find_elements_by_tag_name('tr')[-2].find_elements_by_tag_name('td')[-1]
        ele_date_ele.click()

        '''
        self.driver.find_elements_by_class_name('layui-laydate-content')
        '''

        if python_version3_flag == 'N':
            # 如果是Python2
            random_bank_list = random.choice(cpinfo.bank_list.items())
            self.browser_find_element_by_name('acceptorBankNo').clear()
            self.browser_find_element_by_name('acceptorBankNo').send_keys(random_bank_list[0])

            self.browser_find_element_by_name('acceptorBankName').clear()
            self.browser_find_element_by_name('acceptorBankName').send_keys(random_bank_list[1])
        else:
            # 如果是Python3
            random_bank_list = random.choice(list(cpinfo.bank_list.items()))
            self.browser_find_element_by_name('acceptorBankNo').clear()
            self.browser_find_element_by_name('acceptorBankNo').send_keys(random_bank_list[0])

            self.browser_find_element_by_name('acceptorBankName').clear()
            self.browser_find_element_by_name('acceptorBankName').send_keys(random_bank_list[1])

        self.browser_find_element_by_name('cpAmount').clear()
        self.browser_find_element_by_name('cpAmount').send_keys(random.randrange(100000,500000,step=10000))

        self.browser_find_element_by_name('endorseTimes').clear()
        self.browser_find_element_by_name('endorseTimes').send_keys('0')

        self.browser_find_element_by_name('cpNo').clear()
        self.browser_find_element_by_name('cpNo').send_keys(cpinfo.gen_bill_no())

        self.browser_find_element_by_name('approvalApr').clear()
        self.browser_find_element_by_name('approvalApr').send_keys(random.randint(3,7))

        # self.driver.find_element_by_name('deductAmount').clear()
        # self.driver.find_element_by_name('deductAmount').send_keys('2000')
        # time.sleep(random.randint(1, 3))

        # self.driver.find_element_by_name('turnVolume').clear()
        # self.driver.find_element_by_name('turnVolume').send_keys('99999.50')
        # time.sleep(random.randint(1, 3))

        self.browser_find_element_by_id('publish').click()

        try:
            # 票据发布成功后会弹出确认提示框
            self.browser_webdriverwait_by_clickable(By.CLASS_NAME, "layui-layer-btn0")
            # WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "layui-layer-btn0")))
        except Exception as e:
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "layui-layer-content")))
            except Exception as e:
                print ("票据没有发布成功")
                print ("upload_cp_field AAA type e:", type(e))
            else:
                print ("企业没有完成时实名认证")
        else:
            layui_layer_btn0_text = self.browser_find_element_by_class_name('layui-layer-btn0').text
            if layui_layer_btn0_text == u'确定':
                self.browser_find_element_by_class_name('layui-layer-btn0').click()
            else:
                pass

            try:
                # 票据发布成功后弹出二维码图片
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "layui-layer-title")))
            except Exception as e:
                print ("upload_cp_field BBB error e:", e)
                print ("upload_cp_field BBB type e:", type(e))
            else:
                # 点击关闭二维码图片
                # class_name: layui-layer-ico layui-layer-close layui-layer-close1
                self.browser_find_element_by_class_name('layui-layer-close1').click()

    def publish_cp_many(self):

        pass

    def publish_cp_specific(self):

        pass


def main(frontpic, backpic):

    global LOGIN_SUCCESS_FLAG

    browser = BrowserDriver()
    old_current_url = browser.browser_get_current_url()

    for login_time in range(3):

        if sys.version_info > (3,0):
            IMAGE_FLOW = BytesIO()
        else:
            IMAGE_FLOW = StringIO.StringIO()

        if LOGIN_SUCCESS_FLAG == 'N':
            browser.get_chkcode_image(login_time, IMAGE_FLOW)
            # 使用百度OCR识别图片验证码
            browser.verifycode = baiduocr_img2text(IMAGE_FLOW.getvalue())
            LOGIN_SUCCESS_FLAG = browser.browser_login(login_time)
            IMAGE_FLOW.close()
        else:
            IMAGE_FLOW.close()
            break

    if LOGIN_SUCCESS_FLAG == 'N':
        browser.browser_quit()
    else:
        # browser.browser_login_success_chk()
        # print ("old_current_url:", old_current_url)
        # print ("new_current_url:", browser.browser_get_current_url())

        if browser.browser_get_current_url() != old_current_url:
            browser.browser_choose_company()
        else:
            pass

        browser.browser_move_to_publishpage()
        browser.autoit_upload_cp_pic('uploadImg1', frontpic)
        time.sleep(random.randint(5, 10))
        browser.autoit_upload_cp_pic('uploadImg2', backpic)

        cpinfo = CPData()
        browser.browser_upload_cp_field(cpinfo)
        browser.browser_quit()

if __name__ == '__main__':

    main(CP_FRONT_IMG, CP_BACK_IMG)
