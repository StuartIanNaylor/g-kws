import sox
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input", help="input file name")
args = parser.parse_args()

stat = sox.file_info.stat('audio-rec/orig/silence.wav')
print(stat)
mean_norm_silence = stat['Mean    norm']
print(mean_norm_silence * 125)


dest = "audio-rec/kw/"
filename = os.path.basename(args.input)
print(args.input, filename)
print("sox " + args.input + " audio-rec/orig/temp.wav reverse silence 1 0.15 1% reverse")
print("sox audio-rec/orig/temp.wav " + dest + filename + " silence 1 0.15 1% 1 0.15 1% : newfile : restart")

os.system("sox " + args.input + " audio-rec/orig/temp.wav reverse silence 1 0.15 1% reverse")
os.system("sox audio-rec/orig/temp.wav " + dest + filename + " silence 1 0.15 1% 1 0.15 1% : newfile : restart")




