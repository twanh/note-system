from setuptools import find_packages
from setuptools import setup

setup(
    name='notesystem',
    version='0.0.0',
    description='A tool to help with converting/checking and notes in general',
    url='https://github.com/twanh/note-system',
    author='twanh',
    author_email='huiskenstwan@gmail.com',
    packages=find_packages(exclude=('tests',)),
    python_requires='>=3.8.0',
    install_requires=[
        'mistune>=2.0.0a6',
        'termcolor>=1.1.0',
        'tqdm>=4.56.2',
        'watchdog>=2.0.1',
        'yaspin>=1.4.0',
        'toml==0.10.2',
    ],
    entry_points={
        'console_scripts': [
            'notesystem=notesystem.__main__:run',
        ],
    },
)
