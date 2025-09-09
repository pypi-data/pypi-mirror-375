from setuptools import setup, find_packages

setup(
    name="cti_ctf_challenges",
    version="0.1.2",
    description="cti_ctf_challenges",
    author="foxyjames123_ctf",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",
    ],
    python_requires=">=3.6",
)