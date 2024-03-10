#!/bin/bash

rm -rf package
rm -f *.zip

pip install -t package -r requirements.txt

cd package
zip -r ../lambda_function.zip .
cd ..
zip lambda_function.zip lambda_function.py
