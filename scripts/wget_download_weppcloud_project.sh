#!/bin/bash

# Print the arguments (like "downloading run_id destination")
echo "downloading $1 $2"

# Use curl instead of wget to download the spec file
curl -L "https://wepp.cloud/weppcloud/runs/$1/cfg/aria2c.spec" -o "$1_aria2c.spec"

# Run aria2c with the downloaded spec file
aria2c -j 10 --allow-overwrite=true -d "$2" --input-file="$1_aria2c.spec"