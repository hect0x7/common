from setuptools import setup, find_packages

setup(
    name='common',
    version='0.3.0',
    description='python toolkit for myself',
    author='Straw',
    packages=find_packages(),
    requires=[
        "requests",
        "PyYAML",
        "pyperclip",
        "curl_cffi",
        "tls_client"
    ]
)
