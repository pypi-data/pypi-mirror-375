from setuptools import setup, find_packages

setup(
    name="serpy-rest",
    version="0.1.1",
    description="A minimal ASGI web framework for Python.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Ragav Vignes",
    author_email="ragavvignesviswanathan@gmail.com",
    packages=find_packages(),
    install_requires=["uvicorn"],
    python_requires=">=3.7",
    url="https://github.com/ragav2005/SerPy",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
    ],
    include_package_data=True,
)
