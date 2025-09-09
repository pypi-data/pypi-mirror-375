from setuptools import setup, find_packages
import os

def read(fname):
    """Reads the content of a file relative to the setup.py location."""
    file_path = os.path.join(os.path.dirname(__file__), fname)
    if not os.path.exists(file_path):
        return ""
    with open(file_path, encoding='utf-8') as f:
        return f.read()

NAME = 'sqlalembic'
VERSION = '1.0.0'
DESCRIPTION = 'A comprehensive Python framework for SQLAlchemy model discovery, configuration management, and database migrations with Alembic integration'
LONG_DESCRIPTION = read('README.md') if os.path.exists('README.md') else DESCRIPTION
LONG_DESCRIPTION_CONTENT_TYPE = 'text/markdown'
URL = 'https://github.com/hemaabokila/sqlalembic_framework'
AUTHOR = 'Ibrahem Abokila'
AUTHOR_EMAIL = 'ibrahemabokila@gmail.com'
LICENSE = 'MIT'

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
    'Operating System :: OS Independent',
    'Topic :: Database',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

INSTALL_REQUIRES = [
    'alembic~=1.16.4',
    'PyMySQL~=1.1.1',
    'python-dotenv~=1.1.1',
    'PyYAML~=6.0.2',
    'SQLAlchemy~=2.0.42',
    'toml~=0.10.2',
    'psycopg2-binary~=2.9.10',
]

EXTRAS_REQUIRE = {
    'testing': [
        'pytest~=8.3.5',
    ],
}

ENTRY_POINTS = {
    'console_scripts': [
        'sqlalembic = sqlalembic.main:main',
    ],
}

PACKAGES = find_packages(where='.')

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_CONTENT_TYPE,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    classifiers=CLASSIFIERS,
    packages=PACKAGES,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    entry_points=ENTRY_POINTS,
    include_package_data=True,
    python_requires='>=3.8',
    zip_safe=False,
)