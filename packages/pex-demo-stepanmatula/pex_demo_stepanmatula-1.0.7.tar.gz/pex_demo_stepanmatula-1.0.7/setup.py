from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "A Flask web application built with Jenkins CI/CD pipeline"

setup(
    name='pex-demo-stepanmatula',
    version='1.0.' + os.environ.get('BUILD_NUMBER', '0'),
    description='Flask web application built with Jenkins CI/CD pipeline - PEX Demo',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Stepan',
    author_email='stmatu@softserveinc.com',
    license='MIT',
    url='https://github.com/StepanMatula/pex',
    packages=find_packages(exclude=['tests*', 'deployment*', 'reports*', 'artifacts*']),
    py_modules=['app'],
    include_package_data=True,
    install_requires=[
        'Flask>=3.0.0',
        'gunicorn>=21.2.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'requests>=2.31.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'pex-demo=app:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Framework :: Flask',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    python_requires='>=3.8',
)
