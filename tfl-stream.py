import tensorflow as tf
import sounddevice as sd
import numpy as np
import threading


def sd_callback(rec, frames, time, status):
    global input_details1
    global output_details1
    global inputs1
    global kw_count
    global not_kw_count
    global kw_sum
    global kw_hit
    global kw_max
    global kw_avg
    global kw_probability

    # Notify if errors
    if status:
        print('Error:', status)
    
    rec = np.reshape(rec, (1, 320))
    
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
      if kw_count > 3:
        print(output_data[0][0], output_data[0][1], output_data[0][2], kw_count, kw_sum)
        not_kw_count = 0
        if output_data[0][2] > kw_max:
          kw_max = output_data[0][2]
      kw_count += 1
      kw_sum = kw_sum + output_data[0][2]
      kw_avg = kw_sum / kw_count
      if (kw_sum / kw_avg) / 55 > 1:
        kw_probability = 1.0
      else:
        kw_probability = (kw_sum / kw_avg)  / 55
      if kw_probability > 0.5:
        kw_hit = True
    elif np.argmax(output_data[0]) != 2:
      if not_kw_count > 3:
        if kw_hit == True:
          print("Kw threshold hit", kw_max, kw_avg, kw_probability)
        kw_count = 0
        kw_sum = 0
        kw_hit = False
        kw_max = 0
        kw_probability = 0
        not_kw_count = -1
      not_kw_count += 1


# Parameters
word_threshold = 7.5
word_duration = 10
rec_duration = 0.020
sample_rate = 16000
num_channels = 1
kw_max = 0
kw_avg = 0
kw_probability = 0

sd.default.latency= ('high', 'high')
sd.default.dtype= ('float32', 'float32')


# Load the TFLite model and allocate tensors.
interpreter1 = tf.lite.Interpreter(model_path="/home/pi/g-kws/models2/crnn_state/quantize_opt_for_size_tflite_stream_state_external/stream_state_external.tflite")
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
