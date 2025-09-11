from setuptools import setup, find_packages

exclude_packages = ["wxw.tools", "wxw.tools.*", "wxw.scripts", "wxw.scripts.*"]

setup(
    name="wxw",
    version="1.0.1",
    keywords=["pip", "wxw"],
    description="A library for wxw",
    long_description="Includes some ways to work with pictures, add qt utils",
    author="weixianwei",
    author_email="weixianwei0129@gmail.com",
    url="https://github.com/weixianwei0129/wxwLibrary",
    packages=find_packages(exclude=exclude_packages),
    platforms="any",
    install_requires=[],
)
