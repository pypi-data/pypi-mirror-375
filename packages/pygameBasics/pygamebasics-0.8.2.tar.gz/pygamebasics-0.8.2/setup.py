from setuptools import setup, find_packages

import ast
def getFile(path):
	with open(path, 'r') as rFile:
		tmp = rFile.read()
	return ast.literal_eval(tmp)

with open("README.md", "r", encoding="utf-8") as rFile:
	longDesc = rFile.read()

setup(
	name="pygameBasics",
	version="0.8.2",
	description="pygame Game Engine",
	packages=find_packages(),
	python_requires=">=3.6",
	long_description=longDesc,
	long_description_content_type="text/markdown",
)
