
for file in $(ls *wav)
do
  echo $file
  mv $file temp.wav
  sox temp.wav $file pad 0.2 1
done
