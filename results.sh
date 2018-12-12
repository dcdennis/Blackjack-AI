#! /bin/bash

cp *_results.txt results/

for file in results/*; do

	echo $file
	./average.py $file

done
