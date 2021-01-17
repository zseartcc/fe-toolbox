from setuptools import setup, find_packages

with open("README.md", "rt") as f:
	long_desc = f.read()

setup(
	name="fetools",
	version="1.0.0post1",
	description="Makes some tasks easier for VATUSA FEs.",
	long_description=long_desc,
	long_description_content_type="text/markdown",
	license="GNU GPLv3",
	classifiers=[
		"Programming Language :: Python :: 3"
	],
	keywords="vatsim vrc vstars veram",
	packages=find_packages(),
	python_requires=">=3.6, <4"
)