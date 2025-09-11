from setuptools import setup

NAME = "groupdocs-total-net"
VERSION = "25.9.0"

REQUIRES = ["groupdocs-conversion-net==24.12",
            "groupdocs-viewer-net==24.9",
            "groupdocs-comparison-net==25.6",
            "groupdocs-watermark-net==25.3",
            "groupdocs-metadata-net==25.4",
            "groupdocs-merger-net==25.3",
            "groupdocs-assembly-net==25.5.1",
            "groupdocs-redaction-net==25.5",
            "groupdocs-signature-net==25.4"]

setup(
    name=NAME,
    version=VERSION,
    description='GroupDocs.Total for Python via .NET metapackage that enables you to install all available GroupDocs for Python via .NET products.',
    keywords = [
        "GroupDocs.Total for Python via .NET",
        "GroupDocs for Python via .NET",
        "metapackage",
        "groupdocs-conversion-net",
        "groupdocs-viewer-net",
        "groupdocs-comparison-net",
        "groupdocs-watermark-net",
        "groupdocs-metadata-net",
        "groupdocs-merger-net",
        "groupdocs-assembly-net",
        "groupdocs-redaction-net",
        "groupdocs-signature-net",
        "document conversion",
        "document viewing",
        "document comparison",
        "watermarking",
        "metadata",
        "document merger",
        "document assembly",
        "redaction",
        "digital signature"],
    url='https://products.groupdocs.com/',
    author='GroupDocs',
    author_email='support@groupdocs.com',
    packages=['groupdocs-total-net'],
    include_package_data=True,
    long_description=open("README.md", encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    install_requires=REQUIRES,
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: Other/Proprietary License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS'
    ],
    platforms=[
        'Windows',
        'Linux',
        'macOS',
    ],
    python_requires='>=3.9, <3.12',
)
