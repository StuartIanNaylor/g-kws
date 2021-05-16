import numpy as np
import argparse
import soundfile as sf
import os

parser = argparse.ArgumentParser()
parser.add_argument("--input", help="input file name")
args = parser.parse_args()
outfile = os.path.splitext(args.input)[0]
sig, samplerate = sf.read(args.input)
np.save(outfile + ".npy", sig)
print(sig.shape)

