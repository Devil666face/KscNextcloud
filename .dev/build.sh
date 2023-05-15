#!/bin/bash
./venv/bin/python -m nuitka \
--onefile \
--standalone \
--follow-imports \
--include-plugin-directory=./venv/lib/python3.10/site-packages/apscheduler \
main.py
ARCHIVE_NAME="${PWD##*/}.tgz"
tar -cvzf $ARCHIVE_NAME main.bin
mkdir -p ./dist && mv $ARCHIVE_NAME ./dist