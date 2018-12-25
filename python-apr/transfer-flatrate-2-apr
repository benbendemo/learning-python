#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 11:26:42 2018
@author: jacksonshawn
"""

from __future__ import division
from math import pow

def calc_flat_2_apr(LoanMonthFlatRate, LoanTerms, *LoanAmt):
    
    '''
    calc_flat_2_apr: 根据月平息利率计算实际年利率(APR)

    参数依次为月平息利率, 贷款期限(单位月), 贷款金额
    月平息利率必输, 并且必须是月平息, 不能是年平息
    贷款期限必输
    贷款金额选输
    '''

    if len(LoanAmt) != 0:

        Month_repayment = LoanAmt[0] / LoanTerms + LoanAmt[0] * LoanMonthFlatRate
        Interest_tot = LoanMonthFlatRate * LoanTerms * LoanAmt[0]
        print "Month_repayment is:", Month_repayment
        print "Interest_tot is:", Interest_tot
    
    Max_MPR = 1 / LoanTerms + LoanMonthFlatRate
    
    # 给MPR变量分配一个初始值(根据实际取值的大小预估的初始值)
    MPR = 0.00000001

    while (MPR < Max_MPR):
            
        temp1 = pow((1 + MPR), LoanTerms)
        temp2 = MPR * temp1 / (temp1 - 1) 

        # 因为一元N次(N>=5)方程没有固定求根公式,这里的策略是给定初始值和步长后,
        # 计算出一个误差在可接收范围内最接近正确值的结果出来,这个误差控制参数我将其设置为0.00000001
        if abs(temp2 - Max_MPR) <= 0.00000001:    
            return MPR, Max_MPR
            break
        else:    
            # MPR是一个自增变量,每次增长的步长为0.00000001,这也是一个预估的数值
            MPR = MPR + 0.00000001

if __name__ == "__main__":
    
    # 参数依次为月平息利率, 贷款期限(单位月), 贷款金额
    MPR, Max_MPR = calc_flat_2_apr(0.025/12, 24)
    APR = MPR * 12
    print "MPR is:", MPR
    print "Max_MPR is:", Max_MPR
    print "APR is:",APR
    
