import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mxboxutils",
    version="0.0.3",
    author="RyanLu",
    author_email="lyydev@qq.com",
    description="mxbox utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mxbox/MxBoxUtils",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.12",
)
