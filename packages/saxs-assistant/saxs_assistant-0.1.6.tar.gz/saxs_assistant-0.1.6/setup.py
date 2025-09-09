from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="saxs_assistant",
    version="0.1.6",  # .dev42"
    description="SAXS Assistant: Automated analysis of SAXS data including Guinier, PDDF, and ML-based Dmax prediction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Cesar Ramirez",
    author_email="cr828@scarletmai.rutgers.edu",  # Update this
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={"saxs_assistant": ["models/*.joblib", "music/*.mp3"]},
    install_requires=[
        "pandas==2.2.2",
        "joblib==1.5.1",
        "matplotlib==3.10.3",  # matplotlib==3.10.3  #been using 3.10.3 but for somereason now testpipy says cant
        "numba>=0.59,<0.62",  # "numba==0.61.2",
        "numpy>=2.0.0,<3.0.0",  #        "numpy>=1.26.4,<2.0.0",
        "scikit-learn==1.6.1",
        "scipy==1.15.3",
        "tqdm==4.67.1",
        "openpyxl==3.1.5",
        "pillow==11.2.1",
        "requests>=2.32,<3",
        "natsort",
    ],
    extras_require={"music": ["playsound==1.2.2"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Or your chosen license
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    project_urls={
        "Tutorial": "https://pypi.org/project/saxs-assistant/",
    },
)
