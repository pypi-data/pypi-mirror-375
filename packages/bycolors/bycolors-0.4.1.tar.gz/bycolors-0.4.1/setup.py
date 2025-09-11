"""Install module."""

import setuptools

NAME = "bycolors"
AUTHOR = "kyrylo.gr"
AUTHOR_EMAIL = "git@kyrylo.gr"
DESCRIPTION = "Blue and yellow colors for matplotlib."


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def get_version() -> str:
    with open(f"{NAME}/__config__.py", "r", encoding="utf-8") as file:
        for line in file.readlines():
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    raise ValueError("Version not found")


setuptools.setup(
    name=NAME,
    version=get_version(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kyrylo-gr/b-y-colors",
    packages=setuptools.find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    # install_requires=["matplotlib"],
)
