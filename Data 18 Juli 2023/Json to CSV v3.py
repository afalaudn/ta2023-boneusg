import json
import time
import datetime
import os,glob
import sys,re
import numpy as np
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from scipy.signal import hilbert
import pandas as pd

load_folder = ("E:/Pengolahan Data CD Bone-USG/Json/")
save_folder = ("E:/Pengolahan Data CD Bone-USG/JSON-to-CSV/")

class us_json:
    IDLine = []
    tmp = []
    EnvHil = []
    filtered_fft = []
    LengthT = 0
    filtered_signal = []
    Registers = {}
    t = []
    fPiezo = 5
    Bandwidth = 1.0
    N = 0
    processed = False
    iD = 0

    def JSONprocessing(self, path):
        IDLine = []
        tmp = []

        with open(path) as json_data:
            #DATA = {}
            d = json.load(json_data)
            json_data.close()

            A = d["data"]
            for i in range(int(len(A)/2-1)):
                if (A[2*i+1]) < 128:
                    value = 128*(A[2*i+0]&0b0000111) + A[2*i+1] - 512
                    tmp.append(2.0*value/512.0)
                else:
                    value = 128*(A[2*i+1]&0b111) + A[2*i+2] - 512
                    tmp.append(2.0*value/512.0)
            print("Data acquired")
            self.Registers = d["registers"]
            self.timings = d["timings"]
            self.f = float(64/((1.0+int(d["registers"]["237"]))))

            t = [1.0*x/self.f + self.timings['t4']/1000.0  for x in range(len(tmp))]
            self.t = t

            for i in range(int(len(IDLine))):
                if IDLine[i] < 0:
                    IDLine[i] = 0
            self.LengthT = len(t)

            # Updating the JSON
            self.tmp = tmp
            self.iD = d['experiment']["id"]
            self.N = d['N']
            self.processed = True

    def create_fft(self):
        self.FFT_x = [X*self.f / (self.LengthT) for X in range(int(self.LengthT))]
        self.FFT_y = np.fft.fft(self.tmp)
        self.filtered_fft = np.fft.fft(self.tmp)

        for k in range(int(self.LengthT/2 + 1)):
            if k < (self.LengthT * self.fPiezo * (1 - self.Bandwidth/2.0) / self.f):
                self.filtered_fft[k] = 0
                self.filtered_fft[-k] = 0
            if k > (self.LengthT * self.fPiezo *(1 + self.Bandwidth/2.0) / self.f):
                self.filtered_fft[k] = 0
                self.filtered_fft[-k] = 0

        self.filtered_signal = np.real(np.fft.ifft(self.filtered_fft))

        if self.processed:
            plt.figure(figsize=(15, 5))
            selfLength = int(self.LengthT/2)
            plot_time = self.FFT_x[1:selfLength]
            plot_abs_fft = np.abs(self.FFT_y[1:selfLength])
            plot_filtered_fft = np.abs(self.filtered_fft[1:selfLength])

        self.EnvHil = self.filtered_signal
        self.EnvHil = np.asarray(np.abs(hilbert(self.filtered_signal)))

    def CSV(self):
        if self.processed: #@todo check this to get env & al
            file_names = save_folder+self.iD+str(self.N)+".csv"
            data = pd.DataFrame({"X": self.t , "Y": self.tmp}, index=range(len(self.t))) #"Y": self.tmp = raw, self.filtered_signal = filter, self.EnvHil = enveloppe
            delimiter = ","
            data.to_csv(file_names, index=False, sep=delimiter)

if __name__ == "__main__":
    print("Loaded!")

    json_files = glob.glob(os.path.join(load_folder, "*.json"))

    for filepath in json_files:
        print(os.path.basename(filepath))
        y = us_json()
        y.JSONprocessing(filepath)
        y.create_fft()
        y.CSV()


"""if __name__ == "__main__":
    print("Loaded!")

    for filename in os.listdir(load_folder):
        filepath = os.path.join(load_folder, filename)
        if filename.endswith(".json") and os.path.isfile(filepath):
            print(filename)
            y = us_json()
            y.JSONprocessing(filepath)
            y.create_fft()
            time.sleep(5)  # Tambahkan delay 5 detik di sini
            y.CSV()"""


"""if __name__ == "__main__":
    print("Loaded!")

    for filename in os.listdir(load_folder):
        filepath = os.path.join(load_folder, filename)
        if filename.lower().endswith(".json") and os.path.isfile(filepath):
            print(filename)
            y = us_json()
            y.JSONprocessing(filepath)
            y.create_fft()
            # time.sleep(1)
            y.CSV()"""

"""if __name__ == "__main__":
    print("Loaded!")

    json_files = glob.glob(os.path.join(load_folder, "*.json"))

    for filepath in json_files:
        print(os.path.basename(filepath))
        y = us_json()
        y.JSONprocessing(filepath)
        y.create_fft()
        y.CSV()"""