# import subprocess
import setuptools
# from setuptools.command.build_ext import build_ext

with open("README.md", "r") as fh:
  long_description = fh.read()

# from Cython.Distutils import Extension

# class CMakeBuild(build_ext):
#     def run(self):
#         for ext in self.extensions:
#             self.build_extension(ext)

#     def build_extension(self, ext):
#         if not os.path.exists(self.build_temp):
#             os.makedirs(self.build_temp)

#         extdir = self.get_ext_fullpath(ext.name)
#         if not os.path.exists(extdir):
#             os.makedirs(extdir)

#         # This is the temp directory where your build output should go
#         install_prefix = os.path.abspath(os.path.dirname(extdir))
#         cmake_args = '-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={}'.format(install_prefix)

#         subprocess.check_call(['cmake', ext.sourcedir, cmake_args], cwd=self.build_temp)
#         subprocess.check_call(['cmake', '--build', '.'], cwd=self.build_temp)

setuptools.setup(
  name="easyUI-Qt",
  version="0.0.2",
  author="pitelink",
  author_email="pitelink@outlook.com",
  description="A small example UI package",
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