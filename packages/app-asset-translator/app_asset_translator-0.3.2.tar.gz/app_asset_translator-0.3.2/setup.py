import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='app_asset_translator',
    packages=['app_asset_translator'],
    version='0.3.0',
    license='GNU GPLv3',
    description='Small tool to generate translations files to csv and back',
    long_description=long_description,
    author='Originally by Myler Media, Currently maintained by Stella Schalkwijk',
    url='https://github.com/StellaAlexis/AppAssetTranslator',
    install_requires=['pandas', 'PyYAML'],
    download_url='https://github.com/StellaAlexis/AppAssetTranslator',
    entry_points={
        'console_scripts': [
            'app-asset-translator=app_asset_translator.translator_scripts:main',
        ]
    }
)
