from setuptools import setup, find_packages

setup(
    name='selenium_behave',
    version='1.0.0',
    packages=find_packages(where='selenium_behave'),
    install_requires=[
        'behave',
        'boto3',
        'python-dotenv',
        'PyYAML',
        'requests',
        'allure-behave',
        'selenium',
        'beautifulsoup4',
        'openpyxl',
        'behave-html-formatter',
        'pillow',
        'imagehash',
        # Add any additional dependencies here
    ],
    package_dir={'': 'selenium_behave'},
)