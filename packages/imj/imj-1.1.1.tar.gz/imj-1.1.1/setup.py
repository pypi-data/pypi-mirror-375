import setuptools

setuptools.setup(name="imj",
    version="1.1.1",
    description="Python client for i.marcusj.org",
    long_description=open('README.md','r').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AgeOfMarcus/imj",
    author="AgeOfMarcus",
    author_email="marcus@marcusweinberger.com",
    packages=setuptools.find_packages(),
    zip_safe=False,
    install_requires=[
        'requests',
    ],
)