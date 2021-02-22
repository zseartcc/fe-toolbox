""" IGNORE THIS FILE. INTERNAL UTILITY. """

import subprocess
import shutil
import sys
import os, os.path
import zipapp

reqs = input("Requirements (sep with ','): ").split(",")
fpath = sys.argv[1]
fname = os.path.split(fpath)[1].split('.')[0]

os.mkdir(fname)
os.chdir(fname)

shutil.copyfile(fpath, os.getcwd() + "\\__main__.py")

for r in reqs:
	if r.strip():
		subprocess.check_call([sys.executable, "-m", "pip", "install", r.strip(), "--target", "."])

for f in os.listdir():
	if f.endswith("-info"):
		shutil.rmtree(os.getcwd() + "\\" + f)

os.chdir("..")
zipapp.create_archive(os.getcwd() + "\\" + fname)
shutil.rmtree(os.getcwd() + "\\" + fname)
