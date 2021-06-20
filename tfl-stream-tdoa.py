import tensorflow as tf
import sounddevice as sd
import numpy as np
import threading
import gcc_phat
import soundfile as sf

def sd_callback(rec, frames, time, status):
    global input_details1
    global output_details1
    global inputs1
    global kw_count
    global kw_sum
    global kw_hit
    global kw_avg
    global kw_probability
    global not_kw
    global silence_count
    global silence_hit
    global element
    global channel1
    global channel2
    
    # Notify if errors
    if status:
        print('Error:', status)
    
    #sd.wait()
    channel1 = np.roll(channel1, -320)
    channel2 = np.roll(channel2, -320)
    channel1[len(channel1) - 320:] = rec[:,0]
    channel2[len(channel1) - 320:] = rec[:,1]
    rec = np.reshape(rec[:,0], (1, 320))
    
    # Make prediction from model
    interpreter1.set_tensor(input_details1[0]['index'], rec)
    # set input states (index 1...)
    for s in range(1, len(input_details1)):
      interpreter1.set_tensor(input_details1[s]['index'], inputs1[s])
  
    interpreter1.invoke()
    output_data = interpreter1.get_tensor(output_details1[0]['index'])
    # get output states and set it back to input states
    # which will be fed in the next inference cycle
    for s in range(1, len(input_details1)):
      # The function `get_tensor()` returns a copy of the tensor data.
      # Use `tensor()` in order to get a pointer to the tensor.
      inputs1[s] = interpreter1.get_tensor(output_details1[s]['index'])
     
    if np.argmax(output_data[0]) == 2:
      print(output_data[0][0], output_data[0][1], output_data[0][2], kw_avg, kw_probability, kw_count)
      kw_count += 1
      kw_sum = kw_sum + output_data[0][2]
      kw_avg = kw_sum / kw_count
      kw_probability = kw_avg / 7.5
      silence_count = 0
      if kw_hit == True:
        element += 1
        print(str(element) + " samples")
      if silence_hit == True:
        print('Silence hit')
        silence_hit = False
      if kw_probability > 0.5 and kw_count >= 15:
        if kw_hit == False:
            sf.write('/tmp/kw.wav', channel1, sample_rate, subtype='PCM_16')
            tau, _ = gcc_phat.gcc_phat(channel1, channel2, fs=sample_rate, max_tau=MAX_TDOA, interp=2)
            theta = np.arcsin(tau / MAX_TDOA) * 180 / np.pi
            print(theta)
        kw_hit = True
    elif np.argmax(output_data[0]) == 1:
      not_kw = True
      silence_count = 0
      if silence_hit == True:
        print('Silence hit')
        silence_hit = False
    elif np.argmax(output_data[0]) == 0:
      not_kw = True
      silence_count += 1
      if silence_count >= 10:
        silence_hit = True
      
    if not_kw == True:
      if kw_hit == True:
        print("Kw threshold hit", kw_avg, kw_probability, kw_count)
      kw_count = 0
      kw_sum = 0
      kw_hit = False
      kw_max = 0
      kw_probability = 0
      not_kw = False
      element = 0




# Parameters
word_threshold = 7.5
word_duration = 10
rec_duration = 0.020
sample_rate = 16000
num_channels = 2
kw_avg = 0
kw_count = 0
kw_sum = 0
kw_probability = 0
kw_hit = False
not_kw = False
silence_count = 0
silence_hit = False
SOUND_SPEED = 340.0
MIC_DISTANCE = 0.096
MAX_TDOA = MIC_DISTANCE / float(SOUND_SPEED)
channel1 = np.zeros((int(16000)))
channel2 = np.zeros((int(16000)))
sd.default.latency= ('high', 'high')
sd.default.dtype= ('float32', 'float32')
element = 0

# Load the TFLite model and allocate tensors.
interpreter1 = tf.lite.Interpreter(model_path="/home/stuart/g-kws/models2/ -o0.25-R0.5/quantize_opt_for_size_tflite_stream_state_external/stream_state_external.tflite")
interpreter1.allocate_tensors()

# Get input and output tensors.
input_details1 = interpreter1.get_input_details()
output_details1 = interpreter1.get_output_details()

inputs1 = []

for s in range(len(input_details1)):
  inputs1.append(np.zeros(input_details1[s]['shape'], dtype=np.float32))
    
kw_count = 0
not_kw_count = 0
kw_sum = 0
kw_hit = False



    


# Start streaming from microphone
with sd.InputStream(channels=num_channels,
                    samplerate=sample_rate,
                    blocksize=int(sample_rate * rec_duration),
                    callback=sd_callback):
    threading.Event().wait()