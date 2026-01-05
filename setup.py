from setuptools import setup, find_packages

setup(
    name='hedylang',
    version='0.0.1',
    description='Hedy is a gradual programming language to teach children programming.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Felienne Hermans',
    author_email='felienne@gmail.com',
    packages=find_packages(),
    install_requires=[
        # We cannot go higher than this, because starting 1.2.1+
        # we parse "100" as text instead of a number.
        'lark==1.1.9',
        'iso-639>=0.4.5',
        'iso3166~=2.0.2',
        'Unidecode>=1.4.0',
    ],
    license='EUPL',
    python_requires='>=3.7',
)
