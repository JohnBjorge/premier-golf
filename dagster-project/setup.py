from setuptools import find_packages, setup

setup(
    name="premier_golf_etl",
    packages=find_packages(exclude=["premier_golf_etl_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "boto3",
        "pandas",
        "matplotlib",
        "textblob",
        "tweepy",
        "wordcloud",
    ],
    extras_require={"dev": ["dagit", "pytest"]},
)
