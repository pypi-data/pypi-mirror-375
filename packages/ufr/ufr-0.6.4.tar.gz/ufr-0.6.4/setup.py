from setuptools import setup, Extension
from setuptools.command.install import install

with open("README.md", "r") as fh:
    long_description = fh.read()

# Guardar, talvez seja util futuramente
# import subprocess
# class CustomInstall(install):
#    def run(self):
#        # command = "git clone https://github.com/bombark/linktree"
#        # process = subprocess.Popen(command, shell=True, cwd="packageName")
#        # process.wait()
#        install.run(self)
# module = Extension (
#    '.liblt_api',
#    sources = ['c_code/src/lt_api.c', 'c_code/src/lt_sys.c'],
#    include_dirs = ['c_code/include/'],
#    extra_compile_args=['-fPIC']
# )

setup (
    name="ufr",
    version="0.6.4",
    author="Felipe Bombardelli",
    author_email="felipebombardelli@gmail.com",
    url="https://github.com/VRI-UFPR/ufr",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages = ['ufr'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.6',

    # configure compilation for c code
    # cmdclass={'install': CustomInstall},
    # ext_modules=[module],
    # include_package_data=True,
)
