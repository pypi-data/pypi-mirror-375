from setuptools import setup, find_packages

setup(
    name                          = "tachyons",
    version                       = "1.0.4",
    include_package_data          = True,
    packages                      = find_packages(),
    install_requires              = ["requests"],  # Dependencies
    author                        = "Abdelmathin Habachi",
    author_email                  = "contact@abdelmathin.com" ,
    description                   = "tachyons",
    long_description              = "# Tachyons",
    long_description_content_type = "text/markdown",
    url                           = "https://github.com/Abdelmathin/tachyons",
    classifiers                   = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
