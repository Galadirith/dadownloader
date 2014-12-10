from setuptools import setup, find_packages

setup(
    name        = 'dadownloader',
    version     = '0.1.0',
    description = 'Download your favourite deviations from DeviantArt',
    url         = 'http://github.com/Galadirith/dadownloader',
    license     = 'MIT',
    packages    = find_packages(),
    scripts     = ['bin/dadl'],
    install_requires = ['requests', 'lxml'],
    zip_safe    = False
)
