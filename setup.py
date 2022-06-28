from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name="xgclient",
    version="0.1.3",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    url="https://github.com/oRastor/xgclient",
    license="MIT",
    author="Orest Bduzhak",
    author_email="doom4eg@gmail.com",
    description="PHP client for football (soccer) expected goals (xG) statistics API",
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=["requests", "marshmallow"],
    extras_require={"dev": ["pytest", "requests_mock", "coverage", "mypy"]},
    keywords="football soccer xg expected-goals",
)