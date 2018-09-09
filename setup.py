import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="scpm",
    version="0.1.8",
    author="beanandbean",
    author_email="wangsw.a@gmail.com",
    description="SCons Package Manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/beanandbean/scpm",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
    ],
)
