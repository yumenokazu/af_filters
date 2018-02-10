from setuptools import setup

setup(
    name='af_filters',
    packages=['filter_app'],
    include_package_data=True,
    install_requires=[
        'flask', 'selenium', 'beautifulsoup4',
    ],
)
