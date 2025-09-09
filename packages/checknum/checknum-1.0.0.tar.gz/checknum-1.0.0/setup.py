import setuptools
setuptools.setup(
    name='checknum',
    version='1.0.0',
    author ='Mobin',
    author_email='thelegendaryf14@gmail.com',
    install_requires=[],
    package_dir={"": "checknum"},
    packages=setuptools.find_packages(),
    description='A simple module to calculate averages and check prime numbers',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)