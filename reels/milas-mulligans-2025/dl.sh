#!/bin/bash
SP=$1
while IFS=$'\t' read -r name id; do
  out=$SP/m25/raw/$name.mp4
  for i in 1 2 3; do
    curl -sS -L --fail -o "$out.part" "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t" && mv "$out.part" "$out" && break
    sleep $((2**i))
  done
  echo "$name $(stat -c %s "$out" 2>/dev/null || echo FAIL)"
done < $SP/m25/tools/list.tsv
echo ALLDONE
