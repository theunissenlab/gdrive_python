from setuptools import setup


setup(
    name="gdrive_access",
    version="0.1.1",
    description="Simplified functions for downloading and uploading to Google Drive",
    author="Kevin Yu",
    author_email="kvnyu@berkeley.edu",
    license="MIT License",
    packages=["gdrive_access"],
    entry_points={
        "console_scripts": ["setup_gdrive_credentials = gdrive_access.setup_credentials:run"],
    },
    install_requires=[
        "PyDrive2==1.7.0",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ]
)
