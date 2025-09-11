from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pip_dep_extractor',
    version='2025.9.101642',
    author='Eugene Evstafev',
    author_email='hi@eugene.plus',
    description='Extracts 10 valid Python package names from an LLM response using llmatch.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chigwell/pip_dep_extractor',
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