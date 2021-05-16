for file in $(ls *wav)
do
  echo $file
  python3 audio_vary2.py --input $file
done

