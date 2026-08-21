#!/bin/bash
### PURPOSE OF THIS SCRIPT IS TO TAKE 1/139 EQ CLASSES AND CONSTRUCT the minion script which will then be used to find solutions.
### all i remember so far is like u have to correspond the value of the ith index with 10* what it is, and have the points in there or some shit 
### 2^8 different point vectors, its actually 2^10, since we have a binary string of length 10 but 2 of them will be consequently inferred or something.
rm consistent.min 

#TAKE INPUT 
echo "ENTER EQUIV CLASS:"
read -r EQ
numbers=( $(echo "$EQ" | tr -d '(),') )
echo "PV: ${numbers[@]}"

echo "MINION 3" >> consistent.min
echo "**VARIABLES**" >> consistent.min

# CONSTRUCT ALL 2^8 VARIABLES = 256 POINT TYPES ~=
for ((i=0; i<256; i++)); do
    var=$(printf "%08s\n" "$(echo "obase=2; $i" | bc)")
    echo "BOUND X$var  {0..100}" >> consistent.min
done

exec /Users/ncul0004/codezone/mth3000/minion/bin/minion ./consistent.min