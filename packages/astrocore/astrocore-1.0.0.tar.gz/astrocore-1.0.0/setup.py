import setuptools 

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()
    f.close()

setuptools.setup(
    name='astrocore',
    version='1.0.0',
    author='Neil Ghugare',
    description='Generalized core numerical algorithms originally intended for astrophysical purposes.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/RandomKiddo/astrocore',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={'': 'astrocore'},
    packages=setuptools.find_packages(where='astrocore'),
    python_requires='>=3.9',
    install_requires=['numpy']
)