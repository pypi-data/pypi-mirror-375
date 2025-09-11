from setuptools import setup, find_packages
import io
import os

# Try to read long description from README.md if available
readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
try:
    with io.open(readme_path, 'r', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = ''

setup(
    name='llm_dep_extractor',
    version='2025.9.101648',
    author='Eugene Evstafev',
    author_email='hi@eugene.plus',
    description='Minimal Python package: llm_dep_extractor',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chigwell/llm_dep_extractor',
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    license='MIT',
    tests_require=['unittest'],
    test_suite='test',
)