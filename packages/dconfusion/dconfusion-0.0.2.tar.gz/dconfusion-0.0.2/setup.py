import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="dconfusion",
    version="0.0.2",
    author="Surya Gundavarapu",
    author_email="surya_gundavarapu@yahoo.com",
    description="A package for working with confusion matrices. It can pretty print a confusion matrix, its frequencies and various other metrics.",
    long_description="README.md",
    long_description_content_type="text/markdown",
    url="https://github.com/sgundava/dconfusion",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)