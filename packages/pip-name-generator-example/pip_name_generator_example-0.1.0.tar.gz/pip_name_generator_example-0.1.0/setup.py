from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pip_name_generator_example',
    version='0.1.0',
    description='pip_name_generator: minimal package with a single public function to generate setup.py content.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/chigwell/pip_name_generator',
    author='Eugene Evstafev',
    author_email='hi@eugene.plus',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    license='MIT',
    install_requires=[],
    tests_require=['unittest'],
    test_suite='test',
)