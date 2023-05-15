#!/bin/bash
mkdir python
tar -xf .dev/python-3.10.8-debian10.tgz -C python
tar -xf .dev/pkg.tgz
./python/bin/python3.10 -m venv venv
./venv/bin/pip install --no-index --find-links pkg -r requirements.txt
rm -rf pkg
