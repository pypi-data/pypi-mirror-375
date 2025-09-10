from setuptools import setup, find_packages


def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


setup(
    name='demo137',
    version='0.1.0',
    author='Eugene Evstafev',
    author_email='hi@eugene.plus',
    description='A sample Python package for demonstration purposes.',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/chigwell/demo137',
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
)