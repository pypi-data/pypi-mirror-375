from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-currency-converter-erapi',
    version='1.2.0',
    description='A Django application for currency conversion using real-time exchange rates',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='MD. MAZHARUL ISLAM',
    author_email='mislam@m4a.dev',
    url='https://github.com/mislamdev/django-currency-converter-erapi',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires='>=3.8',
    install_requires=[
        'Django>=3.2,<5.3',
        'requests>=2.25.0,<3.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-django>=4.0',
            'coverage>=5.0',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
        ],
        'dotenv': [
            'python-dotenv>=0.19.0',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Framework :: Django :: 5.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Office/Business :: Financial',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='django currency converter exchange rates api finance',
    project_urls={
        'Bug Reports': 'https://github.com/mislamdev/django-currency-converter-erapi/issues',
        'Source': 'https://github.com/mislamdev/django-currency-converter-erapi',
        'Documentation': 'https://github.com/mislamdev/django-currency-converter-erapi#readme',
    },
)
