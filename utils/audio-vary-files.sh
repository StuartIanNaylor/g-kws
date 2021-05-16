for file in $(ls *wav)
do
  echo $file
  python3 audio_vary.py --input $file
done

