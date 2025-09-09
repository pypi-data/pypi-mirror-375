from setuptools import setup, find_packages

setup(
    name="symmora_001",
    version="0.1.0",
    author="AlexeySimonov",
    description="Just for test purposes",
    long_description=open("README.md").read(),
    url="https://github.com/symmora/symmora_001",
    packages=find_packages(),
    classifiers=[
	"Programming Language :: Python :: 3",
	"License :: OSI Approved :: MIT License",
	"Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
