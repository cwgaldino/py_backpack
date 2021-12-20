import setuptools

setuptools.setup(
    name="py_backpack",
    version="0.1",
    author="Carlos Galdino",
    author_email="galdino@ifi.unicamp.br",
    description="Useful modules and code snippets that I use almost everyday.",
    long_description=open('README.rst').read(),
    long_description_content_type="text/x-rst",
    license='LICENSE.txt',
    url="https://github.com/cwgaldino/py_backpack",
    packages=['backpack'],
    packages_dir={'backpack': './backpack'},
    py_modules=['backpack.arraymanip',
                'backpack.figmanip',
                'backpack.filemanip',
                'backpack.interact',
                'backpack.model_functions'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
