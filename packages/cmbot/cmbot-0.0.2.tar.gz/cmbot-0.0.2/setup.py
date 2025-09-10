from setuptools import setup, find_packages


def read_file(filename):
    with open(filename) as fp:
        return fp.read().strip()


def read_requirements(filename):
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]


name = 'cmbot'
version = '0.0.2'
description = 'A simple RPA framework.'
long_description = open('README.md', encoding='utf-8').read()
author = 'ChenMing'
author_email = 'mling17@163.com'
url = 'https://github.com/mling17'
license = 'MIT'
install_requires = read_requirements('requirements.txt')
setup(
    name=name,  # 项目名，上传到 PyPI 后的包名
    version=version,  # 版本号
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=author,
    author_email=author_email,
    url=url,  # 可选：你的项目主页/GitHub
    packages=find_packages(exclude=['cmbot_bak', 'cmbot_bak.*']),  # 自动查找所有包
    package_data={
        "": ['**/*.pyd',
             '**/*.pyi',
             '__init__.py'
             ],  # 包含编译文件和存根
        'cmbot': ['templates/*.tpl']

    },
    exclude_package_data={
        '': ['*.py', '*.pyc', '*.pyo'],
    },
    install_requires=install_requires,
    license=license,
    classifiers=[
        f'License :: OSI Approved :: {license} License',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
    python_requires='>=3.8',
    include_package_data=True,
    entry_points={
        'console_scripts': ['cmbot=cmbot.cmdline:execute', ],
    },
)
