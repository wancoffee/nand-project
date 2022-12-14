import os
import numpy as np
import csv
import struct
import random
import pandas as pd

#算lefterror 和righterror

pagesize = 18432 # byte
pagenum = 1152
WLnum = 384
pagenum = 4224
WLnum = 1408


# test_name = 'E:/flash_testing/3DV7/New_coding3/0/' + str(68)
# # test_name = 'E:/flash_testing/3DV7/source_files/pattern' + str(14)
# test_file = open(test_name, 'rb')
# test = test_file.read(30)
# print(test)
# exit(0)


# from state value to separate byte in each page
# 8 state values to form 1 byte for each page (total 3 bytes)
def form_byte(v):
    r = np.zeros(3)
    p = 7
    for k in range(8):
        t = v[k]
        for i in range(3):
            b = t % 2
            t = t // 2
            r[2-i] = r[2-i] + b * pow(2, p)
        p = p - 1

    return r

# from 3 bytes to form 8 states
def form_state(L, C, M):
    s = np.zeros(8)
    for i in range(8):
        l = L & pow(2, 7 - i)
        l = l >> (7 - i)

        c = C & pow(2, 7 - i)
        c = c >> (7 - i)

        m = M & pow(2, 7 - i)
        m = m >> (7 - i)

        s[i] = l * 4 + c * 2 + m

    return s


def read_oneWL(file, pagesize):
    LSB = file.read(pagesize)
    CSB = file.read(pagesize)
    MSB = file.read(pagesize)
    ret = np.zeros(pagesize*8)
    for j in range(pagesize):
        # print(LSB[j], CSB[j], MSB[j])
        ret[j*8:j*8+8] = form_state(LSB[j], CSB[j], MSB[j])
    return ret


def process_one_block(index):
    src_name = 'F:/flash_testing/3DV7source_files/pattern' + str(index)
    src_file = open(src_name, 'rb')
    #blk = blk_base + index
    out_name = 'F:/flash_testing/first_nokao/3DV7' + str(119+index) + '/0'
    out_file = open(out_name, 'rb')

    WLnum = 1408
    up_error = np.zeros((WLnum, 7))
    down_error = np.zeros((WLnum, 7))
    state = [7, 6, 4, 0, 2, 3, 1, 5]
    for i in range(WLnum):
        src = read_oneWL(src_file, pagesize)
        out = read_oneWL(out_file, pagesize)
        for j in range(pagesize * 8):
            if src[j] != out[j]:
                idx1 = np.where(state == src[j])
                idx2 = np.where(state == out[j])
                if idx1 < idx2:
                    up_error[i, idx1] = up_error[i, idx1] + 1
                else:
                    down_error[i, idx2] = down_error[i, idx2] + 1
    all_error=up_error+down_error
    MSB_error=all_error[:,2]+all_error[:,6]
    CSB_error=all_error[:,1]+all_error[:,3]+all_error[:,5]
    LSB_error=all_error[:,0]+all_error[:,4]
    return np.max(MSB_error, axis=0),np.max(CSB_error,axis=0),np.max(LSB_error,axis=0)


Num=25
data = pd.DataFrame(np.random.randn(25, 3))
for k in range(Num):
    MSB_error_max,CSB_error_max,LSB_error_max = process_one_block(k)
    data.loc[k,'MSB_error_max']=MSB_error_max
    data.loc[k,'CSB_error_max'] = CSB_error_max
    data.loc[k, 'LSB_error_max'] = LSB_error_max
print(data)
'''
data['page1'] = data.iloc[:,2] + data.iloc[:,6]
data['page2'] = data.iloc[:,1] + data.iloc[:,3] + data.iloc[:,5]
data['page3'] = data.iloc[:,0] + data.iloc[:,4]
'''
to_path='F:\\flash_testing\\first_nokao\\page_errors_max.csv'
data.to_csv(to_path)

print(data)

    
    



'''
blk_base = 70
Num = 1
result = np.zeros((Num, 7))
for k in range(Num):
    up_error, down_error = process_one_block(k)
    result[k, :] = up_error + down_error

print(np.sum(result,axis=1))
# print(up_error.shape)
print(down_error)
print(up_error)
'''
