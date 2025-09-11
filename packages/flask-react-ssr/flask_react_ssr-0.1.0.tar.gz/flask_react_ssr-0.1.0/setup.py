from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='flask-react-ssr',
    version='0.1.0',
    description='A Flask extension for server-side React component rendering using Node.js',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Baraa Khanfar',
    author_email='baraa60@icloud.com',
    url='https://github.com/baraakh30/flask-react',
    packages=find_packages(),
    install_requires=[
        'Flask>=2.0.0',
        'Jinja2>=3.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.10.0',
            'black>=21.0.0',
        ]
    },
    entry_points={
        'console_scripts': [
            'flask-react=flask_react.cli:main',
        ],
    },
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
