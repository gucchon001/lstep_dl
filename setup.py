from setuptools import setup, find_packages

setup(
    name="line_data_downloader",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'selenium>=4.0.0',
        'webdriver-manager>=3.8.0',
        'google-api-python-client>=2.0.0',
        'google-auth-httplib2>=0.1.0',
        'google-auth-oauthlib>=0.4.0',
        'pandas>=1.3.0',
        'requests>=2.26.0',
        'python-dotenv>=0.19.0',
    ],
    entry_points={
        'console_scripts': [
            'line_downloader=src.main:main',
        ],
    },
) 