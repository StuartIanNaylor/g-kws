for file in $(ls *wav)
do
  echo $file
  mv $file temp.wav
  sox temp.wav $file trim 0 00:01  : newfile : restart
done
