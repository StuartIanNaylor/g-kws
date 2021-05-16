for file in $(ls *wav)
do
  echo $file
  mv $file temp.wav
  sox temp.wav $file silence 1 0.17 3% 1 0.17 3% : newfile : restart
done





