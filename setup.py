import setuptools
 
 
with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()
 
 
setuptools.setup(
    name='pybulk',
    version="0.2.4",
    author="pengkailiao",
    author_email="pengkailiao@gmail.com",
    description="PyBulk is a Python module that to allow simple and fast bulk data insertion into databases",
    long_description=long_description, 
    long_description_content_type="text/markdown",
    url="https://github.com/MrLpk/pybulk",
    packages=setuptools.find_packages(),
    
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # 依赖模块
    install_requires=[
        'PyMySQL>=0.9.3',
        'SQLAlchemy>=1.3.8,<=2.0.0',
    ],
    python_requires='>=3.6',
)