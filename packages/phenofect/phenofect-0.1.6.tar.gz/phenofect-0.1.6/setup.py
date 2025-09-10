from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="phenofect",
    version="0.1.6", 
    license='MIT',
    author="Songwon Kim",
    author_email="kimsongwon10@korea.ac.kr",
    description="Package for Forecasting and Exploration of Plant Phenology under Climate Change, which has Parameter Examination, Visualization, Clustering and so on... with Phenological & Meteorological Data.",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/CSBL-urap/2024-summer-swkim",
    packages=find_packages(),
    include_package_data=True, 
    package_data={
        "phenofect": ["Data/*.csv"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    python_requires='>=3.6',
    install_requires=requirements

)
