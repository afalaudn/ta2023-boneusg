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

load_folder = ("C:/Users/Afif Alaudin/Downloads/AMBIL-DATA-06072023/AMBIL-DATA/90%/ATAS/1")
save_folder = ("C:/Users/Afif Alaudin/Downloads/AMBIL-DATA-06072023/AMBIL-DATA/90%/ATAS/1/csv")

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


    def CSV(self):
        if self.processed: #@todo check this to get env & al
            file_names = save_folder+self.iD+"-"+str(self.N)+".csv"
            data = pd.DataFrame({"X": self.t , "Y": self.tmp}, index=range(len(self.t)))
            delimiter = ","
            data.to_csv(file_names, index=False, sep=delimiter)

if __name__ == "__main__":
    print("Loaded!")
    if len(sys.argv) > 1:
        
        if "process" in sys.argv[1]:
            for MyDataFile in os.listdir(load_folder):
                if MyDataFile.endswith(".json"):
                    print(MyDataFile)
                    y = us_json()
                    y.JSONprocessing(load_folder+MyDataFile)
                    y.CSV()
