#!/bin/bash

python3.10 upa3.py --100 --offset $((1 + RANDOM % 10)) -c 20 -p 10 > url_test.txt
python3.10 upa3.py --fetch url_test.txt -l 10 -e 5 -p 10 -c 2
