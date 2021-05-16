
for file in *.wav; do sox "$file" "n10_$file" norm -3; done
