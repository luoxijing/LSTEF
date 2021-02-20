import pandas as pd
import zipfile
from os.path import splitext
import numpy as np
from timers import Timer
import argparse

def wirte_to_file(file_name,real_event_stream,raw_time,width,height):
    f = open(file_name,'w')
    index_t = 0

    f.write(str(width)+' '+str(height)+'\n')
    for i in range(0,len(real_event_stream)):
        for j in range(0,len(real_event_stream[i])):
            no,x,y,p = real_event_stream[i][j]
            t = raw_time[index_t]
            x = int(x)
            y = int(y)
            p = int(p)
            if p != -1:
                f.write(str(t)+' '+str(x)+' '+str(y)+' '+str(p)+'\n')
            index_t += 1
    f.close()
    print('The filtered stream is output to the file:',file_name)
    return 

class FixedDurationEventReader:
    """
    Reads events from a '.txt' or '.zip' file, and packages the events into
    non-overlapping event windows, each of a fixed duration.
    """

    def __init__(self, path_to_event_file, duration_ms=50.0, start_index=0):
        print('Will use fixed duration event windows of size {:.2f} ms'.format(duration_ms))
        print('Output frame rate: {:.1f} Hz'.format(1000.0 / duration_ms))
        file_extension = splitext(path_to_event_file)[1]
        assert(file_extension in ['.txt', '.zip'])
        self.is_zip_file = (file_extension == '.zip')

        if self.is_zip_file:  
            self.zip_file = zipfile.ZipFile(path_to_event_file)
            files_in_archive = self.zip_file.namelist()
            assert(len(files_in_archive) == 1)  
            self.event_file = self.zip_file.open(files_in_archive[0], 'r')
        else:
            self.event_file = open(path_to_event_file, 'r')

        for i in range(1 + start_index):
            self.event_file.readline()

        self.last_stamp = None
        self.duration_s = duration_ms / 1000.0
        self.time = []
        self.flag = 0

    def __iter__(self):
        return self

    def __del__(self):
        if self.is_zip_file:
            self.zip_file.close()

        self.event_file.close()

    def __next__(self):
        with Timer('Reading event window from file'):
            event_list = []
            for line in self.event_file:
                if self.is_zip_file:
                    line = line.decode("utf-8")
                t, x, y, pol = line.split(' ')
                self.time.append(t)
                t, x, y, pol = float(t), int(x), int(y), int(pol)
                event_list.append([t, x, y, pol])
                if self.last_stamp is None:
                    self.last_stamp = t

                if t > self.last_stamp + self.duration_s:
                    self.last_stamp = t
                    event_window = np.array(event_list)
                    return event_window
            if self.flag == 0:
                self.flag = 1
                event_window = np.array(event_list)
                return event_window

        raise StopIteration
