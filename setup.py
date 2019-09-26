from distutils.core import setup

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="JobScraper",
    version="0.0.1",
    author="Alex Lewontin",
    author_email="alex.c.lewontin@gmail.com",
    description="A webscraper for job listings",
    long_description=long_description,
    url="https://github.com/alexclewontin/jobscraper",
    packages=['jobscraper', 'config'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
