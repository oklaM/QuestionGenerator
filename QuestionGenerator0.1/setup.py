"""
@author:xiece
@file: setup.py
@time: 2019/2/13 18:31
"""
import os
from setuptools import setup, find_packages

current_path = os.path.dirname(__file__)


def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    filename = os.path.join(current_path, filename)
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


reqs = parse_requirements('requirements.txt')


read_me_path = os.path.join(current_path, "README.md")
with open(read_me_path, "r", encoding="UTF-8") as fh:
    long_description = fh.read()


setup(
    name='QuestionGenerator',
    version='0.1',
    description="问题生成器模块",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=reqs,
    include_package_data=True,
    zip_safe=False,
    package_data={'QuestionGenerator':['*.csv']}
)
