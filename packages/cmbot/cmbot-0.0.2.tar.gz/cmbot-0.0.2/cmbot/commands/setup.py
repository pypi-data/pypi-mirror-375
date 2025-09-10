# setup.py
from setuptools import setup, find_packages

setup(
    name='cmbot',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'cmbot=commands.cli:execute',
        ],
    },
    install_requires=[
        # 添加依赖项
    ],
    include_package_data=True,
    package_data={
        'commands': ['templates/*.tpl'],
    },
)
