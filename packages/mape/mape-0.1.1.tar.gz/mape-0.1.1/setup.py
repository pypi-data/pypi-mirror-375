from setuptools import setup, find_packages

setup(
    name="mape",
    version="0.1.1",
    author="Takeshi Matsuda",
    author_email="matsuken.tit@gmail.com",
    description="Embedding Method for Structural Preservation via Pairwise Attractiveness",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://www.hannan-u.ac.jp/doctor/i_info-science/matsuda/n5fenj000002lis4.html",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "numpy",
        "pandas",
        "torch",
        "scikit-learn",
        "matplotlib"
    ],
    entry_points={
        "console_scripts": [
            "mape = mape.mape:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Scientific/Engineering :: Mathematics"
    ],
    python_requires=">=3.8"
)