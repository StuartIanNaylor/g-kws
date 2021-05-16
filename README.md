# google-kws

All the kudos here goes to https://github.com/google-research/google-research/tree/master/kws_streaming and really this just exists as it confused why not a seperate repo.

But anyway we are going to have a raspberry Pi focus as the NN models in the above are pretty amazing.

I am going to give some links to some Urls & whl downloads as compiling native is days not hours even and if you don't have a thread ripper or recent I7 prob best as compile is not quick.
Even with the Pip packages if you have a Pi4 but doing a Pi3 install do it on the Pi4 and swap the sd card. (grpcio) can be painfully slow to compile.

X86-64 you should find pip provides the tensorflow & tensorflow addons you need.

# Aarch64 Pi4

First we will do it all in a python venv
Install numpy 1.19.5 `pip install numpy==1.19.5` before installing as possible to get into dependency hell between tensorflow & h5py
```
sudo apt install python3-dev python3-pip python3-venv git
git clone https://github.com/StuartIanNaylor/google-kws.git
cd google-kws
python3 -m venv --system-site-packages ./venv
source ./venv/bin/activate
pip3 install --upgrade pip
pip3 install numpy==1.19.5
```
Then as in https://qengineering.eu/install-tensorflow-2.4.0-on-raspberry-64-os.html but as we are in a venv:-
```
sudo apt-get install gfortran liblapack-dev \
libhdf5-dev libc-ares-dev libeigen3-dev \
libatlas-base-dev libopenblas-dev libblas-dev \
libportaudio2 portaudio19-dev unzip

pip3 install --upgrade setuptools
pip3 install pybind11
pip3 install Cython==0.29.21
pip3 install h5py==2.10.0
pip3 install gdown
pip3 install sounddevice
pip3 install pydot
pip3 install graphviz
pip3 install absl-py
gdown https://drive.google.com/uc?id=1WDG8Rbi0ph0sQ6TtD3ZGJdIN_WAnugLO
pip3 install tensorflow-2.4.1-cp37-cp37m-linux_aarch64.whl
sudo cp asound.conf /etc/
```
The last copies a /etc/asound.conf where you will have to change the index of plughw: to the index of your mic soundcard
Sounddevice doesn't resample so we set 16kHz via a Alsa PCM

You can download my custom dataset dataset.zip
```
gdown https://drive.google.com/uc?id=1w23VFwZK_aHPBnqQE4r5_cb-seZCv8jS
```

# Aarch64 Pi3
Same as above but due to the limited memory we are going to help with some swap.
```
cd ~
git clone https://github.com/StuartIanNaylor/zram-swap-config.git
cd zram-swap-config
sudo ./install.sh
sudo dphys-swapfile swapoff
```
edit so the size is 2048 `CONF_SWAPSIZE=2048` ctrl+x then y to save
```
sudo nano /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
sudo reboot
```

You can now test running the tflite method of TF.
`python3 tfl-stream.py`
To train we need to add tensorflow-addons and compile with bazel

# Install bazel 3.1.0
# Bazel_bin
```
cd ~
git clone https://github.com/PINTO0309/Bazel_bin.git
cd Bazel_bin/3.1.0/Raspbian_Debian_Buster_aarch64/openjdk-8-jdk
gdown https://drive.google.com/uc?id=1VwLxzT3EOTbhSzwvRF2H4ChTQyTQBt3x
sudo dpkg -i adoptopenjdk-8-hotspot_8u222-b10-2_arm64.deb
sudo apt-get update --fix-missing
sudo apt-get install -f
./install.sh
```
You can follow the excellent instructons at https://github.com/PINTO0309/Bazel_bin
But now you can just enter `bazel` at the command prompt to test



# TensorFlow Addons v0.12.1
https://github.com/tensorflow/addons

```
cd ~
wget https://github.com/tensorflow/addons/archive/v0.12.1.zip
unzip v0.12.1.zip
cd addons-0.12.1
```
Now we need to edit configure.py so `sudo nano configure.py`
Change 2 lines to the following:-
```
def is_raspi_arm():
    return (os.uname()[4] == "armv7l") or (os.uname()[4] == "aarch64")  
    
    if is_macos() or is_linux():
#        write("build --copt=-mavx") <-not known in gcc aarch64 
        write("build --cxxopt=-std=c++14")
        write("build --host_cxxopt=-std=c++14")
```
so you should now see somthing like this after running `python3 configure.py`
```
Configuring TensorFlow Addons to be built from source...
> Building only CPU ops

Build configurations successfully written to .bazelrc :

build --action_env TF_HEADER_DIR="/home/pi/google-kws/venv/lib/python3.7/site-packages/tensorflow/include"
build --action_env TF_SHARED_LIBRARY_DIR="/home/pi/google-kws/venv/lib/python3.7/site-packages/tensorflow/python"
build --action_env TF_SHARED_LIBRARY_NAME="_pywrap_tensorflow_internal.so"
build --action_env TF_CXX11_ABI_FLAG="1"
build --spawn_strategy=standalone
build --strategy=Genrule=standalone
build -c opt
build --cxxopt=-std=c++14
build --host_cxxopt=-std=c++14
```
Before we run we will fix the missing lib location with a sym link.
```
sudo ln -s /home/pi/google-kws/venv/lib/python3.7/site-packages/tensorflow/python/_pywrap_tensorflow_internal.so /usr/lib/lib_pywrap_tensorflow_internal.so
```
Now as on https://github.com/tensorflow/addons
```
bazel build build_pip_pkg
bazel-bin/build_pip_pkg artifacts

pip install artifacts/tensorflow_addons-*.whl
```
```
cd ~/google-kws
source setup.txt
```
That will set the env variables
Then choose which NN such as

`source crnn-state-params.txt`
If the training of that model has been run before delete the folder from
`/home/pi/google-kws/models2/`

The models run under TFL with flexdelegates via the full TF binary but you can compile TFL with flexdelegates and the models will run from the standalone TFL binary.


Labels.txt will give you the classification index numbers for silence, other & kw which is the normal order 0,1,2.

Edit the script of tfl-stream.py so the path is correct to the tflite model you have just created in the models2 folder.
`python3 tfl-stream.py`
If the end part of the train fails due to pydot or other dependancies chaning --train to 0 will allow you to run the tests without a full retrain
In kws-streaming/train you will find base_parser.py which has all the training arguments.

I have added --agc which if above 0.0 you can set a different volume for the silence classification than the otherwise used background_volume
Its called --agc as agc is a strange one where silence cab be louder than background as agc will ramp up but between the to you have full control.
--save-audio will pull 10 training sets and output the fingerprints as wavs into the audio folder so you can actually see the audio being fed.

The dataset really requires a minimum of 1000 samples for KW or you may need to up validation / testing % to get a result of 100.

The default is to --resample default=0.15 so with smaller datasets just copy/paste and clone as they will be resampled and create a more varied dataset.
It will work with less but the epoch validation will show zero.
If you have copied and cloned a small dataset into many you may also want to set --volume_resample which is an offset (+- the --volume_resample value)

--silence_percentage, --unknown_percentage is based on KW % and can be used to greatly effect result.
If silence is being hit to much and seems to predominant then lower the %, if not enough then raise.
Same for the unknown category and if KW is not accurate enough lower both to apply more traiing and resultant weight to KW.
Also record a few 1:30 minute samples of your microphone silent with hiss and any constant background noise and add to the __background_noise_ folder

