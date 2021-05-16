for file in $(ls *wav)
do
  echo $file
  sox $file temp.wav silence 1 0.1 2% 1 0.1 2%
  soxi -D temp.wav
done
