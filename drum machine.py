__author__ = 'cook'

import tkinter as tk
from tkinter import filedialog as fd
import tkinter.scrolledtext as tkst
import ttk as ttk
import tkinter.messagebox as messagebox
import os
import time
import threading as thread
import wave
import pickle
import pyaudio as pyaud
from pydub import AudioSegment


class Drum:
    """ Keep track of the various drums """
    current_drum_number = 0
    CHUNK = 1024

    def __init__(self, frame, icon):
        self.drum_no = None
        self.drum_name = None   # name of file without dir info
        self.drum_file_name = None   # full name of file
        self.open_button = tk.Button(frame, image=icon)  # open file btn
        self.open_button.image = icon  # image for open file btn
        self.drum_entry = tk.Entry(frame)  # entry box for open file

    def drum_load(self):
        Drum.current_drum_number = self.drum_no
        try:
            self.drum_file_name = fd.askopenfilename(defaultextension=".wav",
                                                     filetypes=[("WaveFiles", "*.wav")])
            if not self.drum_file_name:
                return
            self.drum_name = os.path.basename(self.drum_file_name)
            self.drum_entry.delete(0, tk.END)
            self.drum_entry.insert(0, self.drum_name)
        except:
            messagebox.showerror('Invalid', self.drum_name+' could not be opened')
            raise


class DrumBeat:
    """Keep track of which beat buttons are clicked"""
    def __init__(self):
        self.btn = None
        self.bpu = None
        self.column = None
        self.row = None

    def button_clicked(self):
        color = 'grey55' if (self.column//self.bpu) % 2 else 'khaki'
        new_color = 'green' if self.btn.cget('bg') != 'green' else color
        self.btn.config(bg=new_color)


class DrumMachine:
    def __init__(self):
        def top_bar():
            self.topframe = tk.Frame(self.root, height=25)
            self.topframe.grid(row=0, columnspan=12, rowspan=self.top_row_height, padx=5, pady=5)
            tk.Label(self.topframe, text='Units:').grid(row=0, column=4)
            self.units_widget = tk.Spinbox(self.topframe, from_=1, to=10, width=5,
                                           textvariable=self.units, command=self.create_right_pad)
            self.units_widget.grid(row=0, column=5)
            tk.Label(self.topframe, text='BPUs:').grid(row=0, column=6)
            self.bpu_widget = tk.Spinbox(self.topframe, from_=1, to=8, width=5,
                                         textvariable=self.bpu, command=self.create_right_pad)
            self.bpu_widget.grid(row=0, column=7)

        def left_bar():
            tk.Label(self.leftframe, text='').grid(row=0, columnspan=6, pady=3)
            for i in range(self.max_drum_num):
                self.drums[i].drum_no = i
                self.drums[i].open_button.config(command=self.drums[i].drum_load)
                self.drums[i].open_button.grid(row=i+1, column=0, padx=5, pady=self.middle_vertical_padding)
                self.drums[i].drum_entry.grid(row=i+1, column=4, padx=7, pady=self.middle_vertical_padding)

        def play_bar():
            self.playframe = tk.Frame(self.root, height=15)
            firstrow = self.top_row_height+self.max_drum_num+1
            self.playframe.grid(row=firstrow, columnspan=13, sticky=tk.W+tk.E, padx=15, pady=10)
            self.playbutton = tk.Button(self.playframe, text='Play',
                                        command=self.play_drums)
            self.playbutton.grid(row=0, column=1, padx=1)
            self.stopbutton = tk.Button(self.playframe, text='Stop',
                                        command=self.stop_drums)
            self.stopbutton.grid(row=0, column=3)
            self.pausebutton = tk.Button(self.playframe, text='Pause',
                                         command=self.pause_drums)
            self.pausebutton.grid(row=0, column=5)
            self.loopcheckbox = tk.Checkbutton(self.playframe, text='Loop', variable=self.loop)
            self.loopcheckbox.grid(row=0, column=16, padx=1)

        self.root = tk.Tk()
        self.root.title('Drum Beast')
        self.max_drum_num = 5
        self.top_row_height = 10
        self.middle_vertical_padding = 2
        self.bpu = tk.IntVar()
        self.bpu.set(4)
        self.units = tk.IntVar()
        self.units.set(4)
        self.loop = tk.BooleanVar()
        self.stop = tk.BooleanVar()
        self.pause = tk.BooleanVar()
        self.loop.set(False)
        self.stop.set(False)
        self.pause.set(False)
        self.p = pyaud.PyAudio()
        self.columns = self.bpu.get()*self.units.get()
        self.leftframe = tk.Frame(self.root)
        self.leftframe.grid(row=self.top_row_height, column=0, columnspan=6, sticky=tk.W+tk.E+tk.N+tk.S)
        tbicon = tk.PhotoImage(file='images/openfile.gif')
        self.drums = [Drum(self.leftframe, tbicon) for x in range(self.max_drum_num)]
        self.beats = [None for x in range(self.columns)]

        top_bar()
        left_bar()
        self.create_right_pad()
        play_bar()
        self.root.mainloop()

    def create_right_pad(self):
        bpu = self.bpu.get()
        units = self.units.get()
        self.columns = bpu*units
        self.rightframe = tk.Frame(self.root)
        self.rightframe.grid(row=self.top_row_height, column=6, sticky=tk.W+tk.E+tk.N+tk.S, padx=15,
                             pady=self.middle_vertical_padding)
        self.beat = [tk.Button(self.rightframe, bg='gray', width=1) for x in range(self.columns)]
        for j in range(self.columns):
            self.beat[j].grid(row=0, column=j)
        self.button = [[DrumBeat() for x in range(self.columns)] for x in range(self.max_drum_num)]
        for i in range(self.max_drum_num):
            for j in range(self.columns):
                color = 'grey55' if (j//bpu) % 2 else 'khaki'
                self.button[i][j].btn = tk.Button(self.rightframe, bg=color, width=1,
                                              command=lambda i=i, j=j: self.mixer(i, j))
                self.button[i][j].btn.grid(row=i+1, column=j)
                self.button[i][j].row = i
                self.button[i][j].column = j
                self.button[i][j].bpu = bpu

    def play_drums(self):
        if self.pause.get():
            self.pause.set(False)
            self.stop.set(False)
        else:
            self.thread = thread.Thread(None, self.play_thread, None, (),{})
            self.thread.start()

    def mixer(self, i, j):
        self.button[i][j].button_clicked()
        self.update_beat()

    def update_beat(self):
        # First we determine which drums are played for each beat,
        # then create a wav file for each beat will all of the drums
        # combined
        self.beats =[None for x in range(self.columns)]
        for j in range(self.columns):
            for i in range(self.max_drum_num):
                if self.drums[i].drum_name and self.button[i][j].btn.cget('bg') == 'green':
                    if self.beats[j] is None:
                        self.beats[j] = AudioSegment.from_wav(self.drums[i].drum_file_name)
                    else:
                        self.beats[j] = self.beats[j].overlay(AudioSegment.from_wav(self.drums[i].drum_file_name), position=0)
            if self.beats[j] is not None:
                self.beats[j].export("mixed_sounds" + str(j)+ ".wav", format="wav")
                wf = wave.open("mixed_sounds" + str(j)+ ".wav", 'rb')
                self.beats[j] = []
                self.beats[j].append(self.p.open(format=self.p.get_format_from_width(wf.getsampwidth()),
                                     channels=wf.getnchannels(),
                                     rate=wf.getframerate(),
                                     output=True))
                self.beats[j].append(wf.readframes(1024))

    def play_thread(self):
        self.p = pyaud.PyAudio()
        self.update_beat()
        self.stop.set(False)
        self.pause.set(False)
        play_at_least_once = True
        while self.loop.get() or play_at_least_once:
            play_at_least_once = False
            for j in range(self.columns):
                if self.stop.get():
                    return
                self.beat[j].config(bg='red')
                while self.pause.get():
                    pass
                if self.beats[j] is not None:
                    self.beats[j][0].write(self.beats[j][1])
                else:
                    time.sleep(1/16.0)
                time.sleep(1/4.0)
                self.beat[j].config(bg='gray')
        self.p.terminate()

    def stop_drums(self):
        self.stop.set(True)

    def pause_drums(self):
        self.pause.set(True)


if __name__ == '__main__':
    dm = DrumMachine()