import wave, os, glob
import sox
import os
count = 0

path = ''
for filename in glob.glob(os.path.join(path, '*.wav')):
  count = count + 1
  
  if count == 2:
   
    os.remove(filename)
    count = 0
