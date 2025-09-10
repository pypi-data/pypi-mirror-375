__author__ = 'Caleb OConnor'

from setuptools import setup, find_packages


with open("README.md", "r") as fh:
    long_description = fh.read()


with open('requirements.txt') as f:
    required = f.read().splitlines()


setup(
    name='medicalimageanalysis',
    author='Caleb OConnor',
    author_email='csoconnor@mdanderson.org',
    version='2.1.86',
    description='Reads in medical images and structures them into 3D arrays with associated ROI/POIs if they exist.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['medicalimageanalysis', 'medicalimageanalysis/read', 'medicalimageanalysis/structure',
              'medicalimageanalysis/utils', 'medicalimageanalysis/utils/convert', 'medicalimageanalysis/utils/image',
              'medicalimageanalysis/utils/mesh', 'medicalimageanalysis/utils/rigid', 'medicalimageanalysis/utils/roi'],
    include_package_data=True,
    url='https://github.com/caleb-oconnor/MedicalImageAnalysis',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
    ],
    install_requires=required,
)
