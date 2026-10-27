#!/bin/bash
exec python3 "$(dirname "$0")/download_with_aria2c.py" "$@"
