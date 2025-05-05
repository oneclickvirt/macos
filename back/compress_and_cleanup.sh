#!/bin/bash
for iso in *.iso; do
  if [[ -f "$iso" ]]; then
    echo "正在压缩: $iso"
    7z a -t7z -m0=lzma2 -mx=9 -mmt=on -ms=on -md=256m "${iso}.7z" "$iso"
    if [[ $? -eq 0 ]]; then
      rm "$iso"
    fi
  fi
done
