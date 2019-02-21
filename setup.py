from setuptools import setup


setup(
    name='bieberhose',
    version='1.0.0',
    description="Collect the latest buzz about 'bieber' from the Twitter firehose",
    long_description=open('README.md').read().strip(),
    author='Gijs van der Voort',
    author_email='vandervoort.gijs@gmail.com',
    license='MIT License',

    packages=['bieberhose'],

    entry_points={
        'console_scripts': [
            'bieberhose=bieberhose.cli:cli',
        ],
    },

    python_requires='>=3.6.0',
    install_requires=[
        'click>=7.0',
        'requests-oauthlib>=1.2.0',
        'requests>=2.21.0',
        'pendulum>=2.0.4',
    ],
    extras_require={
        'dev': [
            'isort==4.3.4',
            'black==18.9b0',
            'flake8==3.7.6',
            'pytest==4.3.0',
        ],
    },
)
