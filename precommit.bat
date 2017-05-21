@echo off
REM We 'cd', else Python's os.getcwd() will return the wrong path
cd precommit

python precommit.py
cd ../