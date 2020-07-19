import setuptools

setuptools.setup(
    name="photoman",
    version="0.0.1",
    author="Maciej Galeja",
    author_email="maciej.galeja@outlook.com",
    description="Photo files manager",
    long_description="Renames photo and video files and creates nice structure for them",
    long_description_content_type="text/plain",
    url="https://github.com/maciejgaleja/good-content",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)