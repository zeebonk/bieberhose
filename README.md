# bieberhose [![Build Status](https://travis-ci.org/zeebonk/bieberhose.svg?branch=master)](https://travis-ci.org/zeebonk/bieberhose)

![bieberhose header](/images/header.png)

Collect the latest buzz about 'bieber' from the Twitter firehose


## Installation

bieberhose requires python>=3.6

Checkout the code:

```bash
git clone git@github.com:zeebonk/bieberhose.git
cd bieberhose
```

Create a new virtual environment via [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):

```bash
mkvirtualenv -a . -p /usr/bin/python3.6 bieberhose
```

And install using pip:

```bash
pip install .
```


## Usage

Before usage, bieberhose needs to be authenticated against the Twitter API.
The authentication data is storted on disk and will be reused in future usage.
Authentication is done via a [Twitter app](https://developer.twitter.com/en/apps),
of which a consumer key and secret need to be passed during authentication. This
can be done via arguments:

```bash
bieberhose authenticate --consumer-key ... --consumer-secret ...
```

Or via environment variables:

```bash
COSUMER_KEY=... CONSUMER_SECRET=... bieberhose authenticate
```

After a succesfull authentication you can collect tweets by running:

```bash
bieberhose collect
```

For more advanced usage, run:

```bash
bieberhose collect --help
```


## Development

Checkout the code:

```bash
git clone git@github.com:zeebonk/bieberhose.git
cd bieberhose
```

Install the package in editable mode and install development extras:

```bash
pip install -e .[dev]
```

Run all checks and tests:

```bash
black bieberhose tests  # Automatic formatter
isort  # Automatic formatter for imports
flake8  # Static checks
pytest  # Tests
```
