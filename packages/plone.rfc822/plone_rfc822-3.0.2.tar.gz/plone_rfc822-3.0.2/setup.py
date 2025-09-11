from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "3.0.2"

long_description = (
    f"{Path('README.rst').read_text()}\n"
    f"{Path('CHANGES.rst').read_text()}\n"
    f"{(Path('src') / 'plone' / 'rfc822' / 'message.rst').read_text()}"
)

setup(
    name="plone.rfc822",
    version=version,
    description="RFC822 marshalling for zope.schema fields",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
    ],
    keywords="zope schema rfc822",
    author="Martin Aspeli and contributors",
    author_email="optilude@gmail.com",
    url="https://pypi.org/project/plone.rfc822",
    license="BSD",
    packages=find_packages("src"),
    namespace_packages=["plone"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    extras_require={
        "supermodel": ["plone.supermodel"],
        "test": [
            "plone.testing",
            "plone.supermodel",
            "zope.annotation",
            "zope.configuration",
            "persistent",
        ],
    },
    install_requires=[
        "python-dateutil",
        "setuptools",
        "zope.component",
        "zope.interface",
        "zope.schema",
    ],
    entry_points="""
    """,
)
