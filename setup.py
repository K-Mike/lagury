import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='lagury',
    version='0.0.1',
    author='Leon Archer, KMike',
    author_email='leon_archer@mail.ru, karchevskymi@gmail.com',
    description='ML workflow manager',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/K-Mike/lagury',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
