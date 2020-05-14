import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "interfacer",
    version = "0.0.1",
    packages=['interfacer'],
    package_data = {'axis-interfacer' : [
        'protocols/axis.json',
        'templates/generate.tcl.j2'
    ]},
    author = "Alex Bucknall",
    author_email = "alex.bucknall@gmail.com",
    description = ("Interfacer is a library for interfacing RTL with SoC designs, primarily for FPGA Partial Reconfiguration development"),
    license = "MIT",
    keywords = ["verilog", "EDA", "hdl", "rtl", "synthesis", "FPGA", "Xilinx", "Partial Reconfiguration"],
    url = "https://github.com/warclab/interfacer",
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU GPLv3 License",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Topic :: Utilities",
    ],
    install_requires=[
        'pyverilog==1.2.0',
        'mkdocs>=1.1',
        'mkdocs-wavedrom-plugin==0.1.1',
        'mkdocs-bibtex==0.2.3',
        'pytest>=3.3.0',
        'Jinja2 >=2.8, !=2.11.0, !=2.11.1',
    ],
    tests_require=[
        'vunit_hdl>=4.0.8'
    ],
    # Supported Python versions: 3.5+
    python_requires=">=3.5, <4",
)