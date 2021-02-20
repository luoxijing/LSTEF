import pandas as pd
import zipfile
from os.path import splitext
import numpy as np
from timers import Timer
import argparse

def filter(Threshold_flag_min,Threshold_flag_max,flag_sum,pix_arr, Pix_Threshold, index_of_event_window, length, real_event_stream, noise_event_pix_num, noise_event_pix_pol, noise_event_num):
    num_noise_sliding_window = []
    for i in range(0,len(flag_sum)):

        if (flag_sum[i][1] <= Threshold_flag_min) & (flag_sum[i][1] > 0) :  
            num_noise_num = filter_by_pix_num(index_of_event_window ,i, flag_sum, pix_arr, Pix_Threshold, length, real_event_stream)
            num_noise_sliding_window.append(num_noise_num)

        if flag_sum[i][1] >= Threshold_flag_max:
            num_noise_num = filter_by_pix_num(index_of_event_window ,i, flag_sum, pix_arr, Pix_Threshold, length, real_event_stream)
            num_noise_sliding_window.append(num_noise_num)

    noise_event_num.append(cal_noise_num(index_of_event_window,real_event_stream))
    print('The number of noise in current events window:',noise_event_num[index_of_event_window])        

    return 

def filter_by_pix_num(index_of_event_window, index_of_sliding_window, flag_sum, pix_arr,Pix_Threshold, length, real_event_stream):
    x,y = flag_sum[index_of_sliding_window][0]
    noise_num = 0
    for i in range(y, y + length):
        for j in range(x, x + length):
            if (i,j) in pix_arr:    
                event_index_list = pix_arr[(i,j)]
                noise = 0   
                for index in event_index_list:
                    if real_event_stream[index_of_event_window][index][3] == -1.0:
                        noise += 1
                total = len(pix_arr[(i,j)])
                pix_num = total - noise

                if pix_num <= Pix_Threshold :
                    for index_of_event in pix_arr[(i,j)]:
                        if real_event_stream[index_of_event_window][index_of_event][3] != -1.0:
                            real_event_stream[index_of_event_window][index_of_event][3] = -1
                            noise_num += 1
    return noise_num

def cal_noise_num(index_window_event,real_event_stream):
    noise_num = 0
    event_num = len(real_event_stream[index_window_event])
    for i in range(0,event_num):
        if real_event_stream[index_window_event][i][3] == -1:
            noise_num+=1
    return noise_num


def cal_pix_threshold(pix_arr):
    pix_threshold = 0
    num_list = [] 
    for pix_coor,event_index_list in pix_arr.items():  
        num_list.append(len(event_index_list))
    num_list.sort(reverse = True) 
    while 0 in num_list:
        num_list.remove(0)
    index_threshold_max = int(len(num_list)) - 1 
    pix_threshold = num_list[index_threshold_max] 
    print('The threshold of noise events:',pix_threshold)
    return pix_threshold
