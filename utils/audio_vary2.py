import sox
import numpy as np
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--input", help="input file name")
args = parser.parse_args()

print(args.input)    
np1 = np.arange(start=-1.0, stop=1.1, step=0.10)
np2 = np.arange(start=0.9, stop=1.11, step=0.01)
np3 = np.arange(start=0.9, stop=1.11, step=0.01)
np4 = np.arange(start=-5.0, stop=5.5, step=0.5)

np.random.shuffle(np1)
np.random.shuffle(np2)
np.random.shuffle(np3)
np.random.shuffle(np4)

x = 0
command ='mv ' + args.input + ' temp.wav'
os.system(command)

while x < 21:
  tfm1 = sox.Transformer()
  pitch_offset = round(np1[x],1)
  tempo_offset = round(np2[x],1)

  gain_offset = round(np4[x],1)
    
  tfm1.pitch(pitch_offset)
  tfm1.gain(gain_offset, False)      
  tfm1.tempo(tempo_offset, 's')

  tfm1.build_file('temp.wav', 'pp' + str(x) + '-' + args.input)
  
  x = x + 1
