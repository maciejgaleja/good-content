#!/bin/bash -e

rm -rf dist || true
rm -rf photoman.egg-info || true
python3 setup.py sdist
python3 -m pip install --user dist/photoman-*.tar.gz