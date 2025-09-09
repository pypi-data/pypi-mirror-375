import setuptools

# version_meta = runpy.run_path("./version.py")

def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="easyUI-Qt",
  version="0.0.4",
  author="彭冲",
  author_email="pitelink@outlook.com",
  description="A small UI package",
  long_description=long_description,
  long_description_content_type="text/markdown",
  install_requires=parse_requirements("requirements.txt"),
  url="",
  packages=setuptools.find_packages(), #需要打包的python源码
  classifiers=[
  "Programming Language :: Python :: 3.11",
  "License :: OSI Approved :: MIT License",
  "Operating System :: Microsoft :: Windows",
  ]
)