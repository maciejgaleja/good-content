rmdir /S /Q dist
python setup.py sdist

cd dist
for /r %%i in (./*) do pip install %%i
cd ..
