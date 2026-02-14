#!/bin/bash

# Print the arguments (like "downloading run_id destination")
echo "downloading $1 $2"

# Read JWT token from ~/.weppcloud_jwt if it exists
JWT=""
if [ -f "$HOME/.weppcloud_jwt" ]; then
    JWT=$(cat "$HOME/.weppcloud_jwt" | tr -d '[:space:]')
fi

if [ -n "$JWT" ]; then
    echo "using JWT authentication"
    curl -L -H "Authorization: Bearer $JWT" "https://wepp.cloud/weppcloud/runs/$1/cfg/aria2c.spec" -o "$1_aria2c.spec"
    aria2c -j 10 --allow-overwrite=true -d "$2" --header="Authorization: Bearer $JWT" --input-file="$1_aria2c.spec"
else
    echo "no JWT token found at ~/.weppcloud_jwt"
    echo "downloading without authentication"
    curl -L "https://wepp.cloud/weppcloud/runs/$1/cfg/aria2c.spec" -o "$1_aria2c.spec"
    aria2c -j 10 --allow-overwrite=true -d "$2" --input-file="$1_aria2c.spec"
fi
