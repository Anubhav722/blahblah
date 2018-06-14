
# cautious-octo-scanner

Cautious Octo Scanner is a Django app that extracts Basic and Github/StackOverflow/Linkedin details of a user from files like .pdf, .doc, .docx.

## Installation

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

## Built With

* [Python 2.7](http://www.python.org/) - Programming Language used.
n* [Django](https://www.djangoproject.com/) - The web framework used.
* [Apache Maven](https://maven.apache.org/) - Dependency Management.
* [Apache Tika](https://tika.apache.org/) - Toolkit for detecting and extracting metadata.
* [NLTK](http://www.nltk.org/) - Natural Language Processing package for Python.

### Prerequisites

Libraries you need to install before setting the Resume Parser environment.

- Tessaract-ocr

```
sudo apt-get install tessaract-ocr
sudo apt-get install tesseract-ocr-eng
sudo apt-get install tesseract-ocr-osd
sudo apt-get install tesseract-ocr-equ
```

- Antiword

```
sudo apt-get install antiword
```
- Pandoc

```
sudo apt-get install pandoc
```

- Apache Maven

```
Installation Instructions: (http://maven.apache.org/install.html)
```

- If exceptions are thrown:

Refer to this article: (https://github.com/tesseract-ocr/tesseract/wiki/Compiling)

And install the following libraries:

```
sudo apt-get install autoconf automake libtool
sudo apt-get install libpng12-dev
sudo apt-get install libjpeg62-dev
sudo apt-get install libtiff4-dev
sudo apt-get install zlib1g-dev
sudo apt-get install python-dev libxml2-dev libxslt1-dev zlib1g-dev
```

- Cloning Existing Repository

 * [cvParser](https://github.com/DewarM/cvParser) - cvParser by DewarM

 * [ResumeParser](https://github.com/antonydeepak/ResumeParser) - ResumeParser by Antony Deepak

- Adding path in parser.env
 -- Edit parser.env and add the path of above cloned repos.

### Installing

- Creating an environment for resume parser.

```
virtualenv <environment-name>
```

- Activating the virtual environment name.

```
source <environment-name>/bin/activate
```

- Sourcing parser.env

Change directory where parser.env is present.

```
source parser.env
```

- Installing requirements.txt

```
pip install -r requirements/dev.txt
```

- Downloading NLTK data:

Go to a python shell.

```
import nltk
nltk.download()
d # select d to go to downloads
all # type all to download all packages.
```

If a popup opens, select all and click on download.

## Other Helpful Articles
(https://gist.github.com/IaroslavR/834066ba4c0e25a27078)
(https://pythontips.com/2016/02/25/ocr-on-pdf-files-using-python/)
(http://www.oracle.com/technetwork/java/javase/downloads/index.html) - [JAVA JDK for Apache Tika]

## Changing Policy in ImageMagick

Change directory to `/etc/ImageMagick-6/`
Edit `policy.xml`
Comment the line - `<policy domain="delegate" rights="none" pattern="HTTPS" />`

## Repo structure
	NOTE: The directory which contains `manage.py` is considered to be root directory of the project. Every directory we explain below is relative to the root directory.
	.
	-- README
	-- parser.env.template
	+-- docs
	|   --- extraction.md
	|   --- ranking-system.md
	+-- api-docs
	|   --- Makefile
	|   --- make.bat
	|   +-- build
	|   +-- src
	+-- requirements
	|   +-- common.txt
	|   +-- dev.txt
	|   +-- staging.txt
	|   +-- production.txt
	+-- jarvis
	|   +-- settings
	|   +-- core
	|   +-- resume
	|   +-- accounts
	|   +-- skills
	|   +-- jarvis


docs: Contains the copy of understanding docs
api-docs: Contains `spnix` documentation of api endpoints
Requirements: Contains `pip` requirements based on the environment (e.g: dev, staging, production.)
jarvis: Main django module consists of all the django apps. It also has `settings` module
  * accounts: deals with users and userprofile
  * resume: core part of the project, which deals with extraction and ranking of the resume
  * skills: exposes endpoints to find the skill similarity
  * core: contains some common utils that get shared between all other apps

## Viewing API docs

```bash
	$ pip install sphinx
	$ pip install sphinxcontrib-httpdomain
	$ cd api-docs
	$ make html source build/html
```

Open `build/html/index.html` to start navigating the docs.

# potential-scanner


