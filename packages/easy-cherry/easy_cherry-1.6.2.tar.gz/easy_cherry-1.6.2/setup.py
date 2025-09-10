from setuptools import setup, find_packages

setup(
    name='easy_cherry',
    version='1.6.2',
    author='vinay kr',
    author_email='vinay.me223@gmail.com',
    description='A custom wrapper for the Slack SDK to simplify sending messages and files.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    #url='https://github.com/yourusername/slack-custom-notifier', # Optional: Add your repo URL
    packages=find_packages(),
    install_requires=[
        'slack_sdk>=3.0.0',
        'html2text>=2020.1.16' # Dependency for HTML conversion
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        "Intended Audience :: Developers",
        "Topic :: Communications :: Chat",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires='>=3.8',
)

