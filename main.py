import pandas as pd
import zipfile
from os.path import splitext
import numpy as np
from timers import Timer
import argparse
from filters import filter,filter_by_pix_num,cal_pix_threshold
from util_io import wirte_to_file, FixedDurationEventReader 
import math

if __name__ =="__main__":

    parser = argparse.ArgumentParser(description = 'Filtering a event stream')
    parser.add_argument('-i','--input_file',required=True, type=str, help='path to input event file')
    parser.add_argument('-o','--output_file',required=True, type=str, help='path to output event file')
    args = parser.parse_args()

    path_to_events = args.input_file
    duration_ms = 50.0
    start_index = 0
    header = pd.read_csv(path_to_events,delim_whitespace=True, header=None, names=['width', 'height'],
                            dtype={'width': np.int, 'height': np.int},
                            nrows=1)

    width, height = header.values[0]

    event_window_iterator = FixedDurationEventReader(path_to_events, duration_ms = duration_ms,start_index = start_index)
    print(event_window_iterator)
        
    length = 5
    stride = 2

    real_event_stream = [] 
    noise_event_num = [] 
    noise_event_pix_num = []
    noise_event_pix_pol = []

    index_of_event_window = -1   

    for event_window in event_window_iterator:
        index_of_event_window += 1
        print('==================The index of event_window:',index_of_event_window + 1,'======================')
        real_event_stream.append(event_window) 
        print('event_window.shape:',event_window.shape)

        flag_arr = np.zeros((height,width),dtype = int)
        pix_arr = {} 

        i = 0
        for event in event_window:
            x = int(event[2])
            y = int(event[1])
            flag_arr[x][y] = 1

            if (x,y) not in pix_arr:
                pix_arr[(x,y)] = []
            pix_arr[(x,y)].append(i)
            i += 1
                    
        index_X = range(0, width + 1 - length, stride)
        index_Y = range(0, height + 1 - length, stride) 

        Threshold_flag_min = 3
        Threshold_flag_max = 0
        num_list = []   
        flag_sum = [] 

        for index_y in index_Y:
            for index_x in index_X:
                num = 0    
                for i in range(index_y,index_y + length): 
                    for j in range(index_x,index_x + length):
                        if flag_arr[i][j] == 1:
                            num += 1
                num_list.append(num)
                flag_sum.append([(index_x,index_y),num])


        num_list.sort(reverse = True)
        while 0 in num_list:
            num_list.remove(0)
        index_min = int(len(num_list) * 0.9) - 1
        if Threshold_flag_min < num_list[index_min]:  
            Threshold_flag_min = num_list[index_min]    
        Threshold_flag_max = math.ceil(length * length * 0.9) 
        print('The candidate threshold of sparse/dense noise :',Threshold_flag_min,'-',Threshold_flag_max)
        Pix_Threshold = cal_pix_threshold(pix_arr)

        filter(Threshold_flag_min,Threshold_flag_max,flag_sum, pix_arr, Pix_Threshold, index_of_event_window, length, real_event_stream, noise_event_pix_num, noise_event_pix_pol, noise_event_num)
        
    raw_time = event_window_iterator.time

    print('The number of filtered events:',sum(noise_event_num))

    output_file = args.output_file
    wirte_to_file(output_file,real_event_stream,raw_time, width, height)

