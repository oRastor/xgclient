from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name="xgclient",
    version="0.1.8",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    url="https://github.com/oRastor/xgclient",
    license="MIT",
    author="Orest Bduzhak",
    author_email="doom4eg@gmail.com",
    description="Python client for football (soccer) expected goals (xG) statistics API",
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=["requests~=2.28.0", "marshmallow~=3.16.0", "pandas~=1.3.5"],
    extras_require={"dev": ["pytest", "requests_mock", "coverage", "mypy"]},
    keywords="football soccer xg expected-goals",
)