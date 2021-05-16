for file in $(ls *wav)
do
  echo $file
  sox $file -r 16000 xx-$file
  rm $file
done
