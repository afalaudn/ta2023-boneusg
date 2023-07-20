# Mengimpor modul-modul yang diperlukan
import json
import time
import datetime
import os
import glob
import sys
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import hilbert
import pandas as pd

# Menentukan folder untuk memuat data JSON dan folder untuk menyimpan data CSV
load_folder = ("E:/AMBIL-DATA/JSONtoCSV/")
save_folder = ("E:/AMBIL-DATA/csv/")

# Membuat class us_json yang akan digunakan untuk memproses data JSON dan melakukan konversi ke CSV.
class us_json:
    # Mendefinisikan atribut-atribut yang akan digunakan untuk menyimpan data sementara.
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

    # Metode untuk memproses data JSON
    def JSONprocessing(self, path):
        IDLine = []
        tmp = []

        # Membuka file JSON dan memuatnya sebagai objek python menggunakan json.load()
        with open(path) as json_data:
            # Membaca data dari file JSON dan menyimpannya di dalam variabel 'd'
            d = json.load(json_data)
            json_data.close()

            # Mengambil data 'data' dari 'd' yang merupakan bagian array dari objek JSON
            A = d["data"]
            for i in range(int(len(A)/2-1)):
                # Memproses data A menjadi bentuk nilai yang sesuai
                if (A[2*i+1]) < 128:
                    value = 128*(A[2*i+0]&0b0000111) + A[2*i+1] - 512
                    tmp.append(2.0*value/512.0)
                else:
                    value = 128*(A[2*i+1]&0b111) + A[2*i+2] - 512
                    tmp.append(2.0*value/512.0)
            print("Data acquired")
            
            # Mengambil data 'registers' dan 'timings' dari 'd' sebagai atribut di dalam class
            self.Registers = d["registers"]
            self.timings = d["timings"]
            # Menghitung nilai 'f' berdasarkan nilai dari 'registers' yang diambil sebelumnya
            self.f = float(64/((1.0+int(d["registers"]["237"]))))
            
            # Menghitung nilai 't' berdasarkan data 'tmp' dan 'timings'
            t = [1.0*x/self.f + self.timings['t4']/1000.0  for x in range(len(tmp))]
            self.t = t
            
            # Proses lainnya untuk data IDLine dan LengthT
            for i in range(int(len(IDLine))):
                if IDLine[i] < 0:
                    IDLine[i] = 0
            self.LengthT = len(t)            

            # Mengupdate data sementara yang telah diproses sebelumnya
            self.tmp = tmp
            self.iD = d['experiment']["id"]
            self.N = d['N']
            self.processed = True

    # Metode untuk membuat transformasi Fourier dari data
    def create_fft(self):
        self.FFT_x = [X*self.f / (self.LengthT) for X in range(int(self.LengthT))]
        self.FFT_y = np.fft.fft(self.tmp)
        self.filtered_fft = np.fft.fft(self.tmp)

        # Proses lainnya untuk filter FFT

        for k in range(int(self.LengthT/2 + 1)):
            if k < (self.LengthT * self.fPiezo * (1 - self.Bandwidth/2.0) / self.f):
                self.filtered_fft[k] = 0
                self.filtered_fft[-k] = 0
            if k > (self.LengthT * self.fPiezo *(1 + self.Bandwidth/2.0) / self.f):
                self.filtered_fft[k] = 0
                self.filtered_fft[-k] = 0

        self.filtered_signal = np.real(np.fft.ifft(self.filtered_fft))
        
        # Proses lainnya untuk filtered_signal
        if self.processed:
            plt.figure(figsize=(15, 5))
            selfLength = int(self.LengthT/2)
            plot_time = self.FFT_x[1:selfLength]
            plot_abs_fft = np.abs(self.FFT_y[1:selfLength])
            plot_filtered_fft = np.abs(self.filtered_fft[1:selfLength])
        
        # Proses lainnya untuk EnvHil
        self.EnvHil = self.filtered_signal
        self.EnvHil = np.asarray(np.abs(hilbert(self.filtered_signal)))

    # Metode untuk menyimpan data hasil proses dalam file CSV
    def CSV(self):
        if self.processed: #@todo check this to get env & al
            # Membuat nama file CSV berdasarkan atribut iD dan N dari data yang telah diproses
            file_names = save_folder+self.iD+"-"+str(self.N)+".csv"
            # Membuat objek DataFrame dengan data 't' dan 'tmp' yang telah diproses sebelumnya
            # #"Y": self.tmp = raw, self.filtered_signal = filter, self.EnvHil = enveloppe
            data = pd.DataFrame({"X": self.t , "Y": self.tmp}, index=range(len(self.t)))
            # Menyimpan DataFrame menjadi file CSV dengan menggunakan tanda ',' sebagai delimiter
            delimiter = ","
            data.to_csv(file_names, index=False, sep=delimiter)

# Bagian ini akan dieksekusi ketika script dijalankan sebagai program utama
if __name__ == "__main__":
    # Mencetak pesan "Loaded!" untuk menandakan bahwa program telah dimuat.
    print("Loaded!")
    
    # Mencari semua file dengan ekstensi .json dalam folder load_folder menggunakan glob.glob
    json_files = glob.glob(os.path.join(load_folder, "*.json"))

    # Melakukan perulangan untuk setiap jalur file JSON yang ditemukan dalam json_files
    for filepath in json_files:
        # Mencetak nama file JSON yang sedang diproses
        print(os.path.basename(filepath))
        
        # Membuat objek y dari class us_json.
        y = us_json()

        # Memanggil metode JSONprocessing dengan memberikan jalur file JSON sebagai argumen.
        # Metode ini akan memproses data JSON dan mengisi atribut objek y dengan data yang diambil dari file JSON tersebut.
        y.JSONprocessing(filepath)

        # Memanggil metode create_fft untuk membuat transformasi Fourier dari data yang telah diproses sebelumnya.
        y.create_fft()

        # Memanggil metode CSV untuk menyimpan data hasil proses ke dalam file CSV.
        y.CSV()

