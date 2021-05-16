import sox
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--input", help="input file name")
args = parser.parse_args()

print(args.input)    
np1 = np.arange(start=-1.0, stop=1.1, step=0.20)
np2 = np.arange(start=0.9, stop=1.11, step=0.02)
np3 = np.arange(start=0.9, stop=1.11, step=0.02)
np4 = np.arange(start=-5.0, stop=5.5, step=0.5)

np.random.shuffle(np1)
np.random.shuffle(np2)
np.random.shuffle(np3)
np.random.shuffle(np4)

tfm = sox.Transformer()
tfm.silence(1, 0.1, 0.01)
tfm.silence(-1, 0.1, 0.01)
tfm.build_file(args.input, 'silence-strip.wav')
stat = sox.file_info.stat('silence-strip.wav')
print(stat)
duration = stat['Length (seconds)']


x = 0

while x < 21:
  tfm1 = sox.Transformer()
  pitch_offset = round(np1[x],1)
  tempo_offset = round(np2[x],1)
  pad_offset = round(np3[x],1)
  gain_offset = round(np4[x],1)
    
  tfm1.norm(-3)
  tfm1.pitch(pitch_offset)
  pad = (1 - duration)
  startpad = abs(pad * pad_offset) / 2
  endpad = pad - startpad  
  
  tfm1.gain(gain_offset, False)      
  tfm1.tempo(tempo_offset, 's')
  tfm1.pad(startpad, endpad)
  tfm1.trim(0, 1)
  tfm1.build_file('silence-strip.wav', 'pp' + str(x) + '-' + args.input)
  
  x = x + 1
