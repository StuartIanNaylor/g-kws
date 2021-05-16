for file in $(ls *wav)
do
  echo $file
  python3 wav2numpy.py --input $file
done
