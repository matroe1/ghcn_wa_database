import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ghcn_wa_database", # Replace with your own username
    version="0.0.1",
    author="Matt Roe",
    author_email="matthew.a.roe@gmail.com",
    description=("Tools to build and access a local SQLite database from the \
                GHCN daily observations data at stations in Washington State, \
                USA"),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matroe1/ghcn_wa_database",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
    python_requires='>=3.6',
)
