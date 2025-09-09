import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="easyUI-Qt",
  version="0.0.3",
  author="彭冲",
  author_email="pitelink@outlook.com",
  description="A small UI package",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="",
  packages=setuptools.find_packages(),
  classifiers=[
  "Programming Language :: Python :: 3.11",
  "License :: OSI Approved :: MIT License",
  "Operating System :: Microsoft :: Windows",
  ]
)