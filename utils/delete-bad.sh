for file in $(ls *wav)
do
  #echo $file
  sox $file temp.wav silence 1 0.15 1% 1 0.15 1%
  DUR=$( { soxi -D 'temp.wav'; } 2>&1);
  RESULT=$(echo $DUR"<0.40" | bc)
  if [ "$RESULT" -eq 1 ]; then
      rm $file
      echo $file
  fi
done
