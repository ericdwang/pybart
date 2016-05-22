from setuptools import setup


with open('README.rst') as readme:
    long_description = readme.read()

setup(
    name='pybart',
    version=__import__('pybart').__version__,
    description=(
        'Real time BART (Bay Area Rapid Transit) information in your '
        'terminal!'),
    long_description=long_description,
    author='Eric Wang',
    author_email='gnawrice@gmail.com',
    url='https://github.com/ericdwang/pybart',
    packages=['pybart'],
    entry_points={'console_scripts': ['bart = pybart.main:main']},
    classifiers=[
        'Environment :: Console :: Curses',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    license='BSD 3-Clause',
    keywords=['bart', 'bay', 'area', 'rapid', 'transit'],
)
