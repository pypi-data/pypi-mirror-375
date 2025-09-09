from subprocess import run

run("cd python/source && python3 setup.py build_ext --build-lib=\"../lib\"", shell=True)
