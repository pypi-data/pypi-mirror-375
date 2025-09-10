[![DOI](https://zenodo.org/badge/993095977.svg)](https://doi.org/10.5281/zenodo.16531481)


# Research Software Fairness Checks (RSFC)

A command line interface to automatically evaluate the quality of a Github or Gitlab repository.

**Authors**: Daniel Garijo, Andrés Montero


## Features

Given a repository URL, RSFC will perform a series of checks based on a list of research software quality indicators (RSQI). The RSQIs currently covered by the package are:

- software_has_license
- software_has_citation
- has_releases
- repository_workflows
- version_control_use
- requirements_specified
- software_documentation
- persistent_and_unique_identifier
- descriptive_metadata
- software_tests
- archived_in_software_heritage
- versioning_standards_use

For more information about these RSQIs, you can check https://github.com/EVERSE-ResearchSoftware/indicators. We have plans to implement all of the RSQIs available in that repository.


## Requirements

Python 3.10.8 or higher

Dependencies are available in the requirements.txt or pyproject.toml file located in the root of the repository

## Install from PyPI

Just run in your terminal the following command:

```
pip install rsfc
```

## Install from Github with Poetry

To install the package, first clone the repository in your machine.
This project uses Poetry for dependency and environment management.

```
git clone https://github.com/oeg-upm/rsfc.git
```

Go to the project's root directory

```
cd rsfc
```

Install Poetry (if you haven’t already)

```
curl -sSL https://install.python-poetry.org | python3 -
```

Make sure Poetry is available in your PATH

```
poetry --version
```

Create the virtual environment and install dependencies

```
poetry install
```

Activate the virtual environment (Optional)

```
source $(poetry env info --path)/bin/activate
```

Your terminal prompt should now show something like:

```
(rsfc-py3.11) your-user@your-machine rsfc %
```

With virtual environment activated you can tried like this:

```
rsfc --help
```

Without poetry virtual environment activated you need to use the poetry run:

```
poetry run rsfc --help
```

## Docker installation

If preferred, RSFC can be executed using docker.

Once you have cloned the repository, go to the project's root directory and run the following command to build the image:

```
docker build -t rsfc-docker .
```

After that, it is necessary to create the directory in which the output assessment will be saved. You can do it by running the following command:

```
mkdir ./outputs
```

Finally, run the following command to run the container:

```
docker run --rm -v $(pwd)/outputs:/rsfc/outputs rsfc-docker <repo_url>
```

where repo_url is the url of the repository to be analyzed, which is strictly needed.

## Usage

After installation, you can use the package by running if you activated the poetry env

```
rsfc <repo_url>
```

or like this without the poetry env

```
poetry run rsfc <repo_url>
```
