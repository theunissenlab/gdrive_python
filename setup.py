from setuptools import setup


setup(
    name="gdrive_access",
    version="0.0.2",
    description="Simplified functions for downloading and uploading to Google Drive",
    author="Kevin Yu",
    author_email="kvnyu@berkeley.edu",
    license="MIT License",
    packages=["gdrive_access"],
    install_requires=[
        "PyDrive==1.3.1",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ]
)
