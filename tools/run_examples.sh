#!/bin/bash -uxe

pushd example/

# Prepare news20 dataset.
if [ ! -f news20 ]; then
  wget "https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/multiclass/news20.bz2"
  bzip2 -d news20.bz2
fi

if [ ! -f news20.t ]; then
  wget "https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/multiclass/news20.t.bz2"
  bzip2 -d news20.t.bz2
fi

# Run example programs.
for CODE in *.py; do
  python "${CODE}"
done

popd

echo "OK"
