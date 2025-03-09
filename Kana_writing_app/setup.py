from setuptools import setup, find_packages

setup(
    name="kana-writing-practice",
    version="1.0.0",
    description="An AI-powered application for practicing Japanese kana writing",
    author="Your Name",
    author_email="email@example.com",
    packages=find_packages(),
    install_requires=[
        "streamlit==1.32.0",
        "Pillow==10.1.0",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
        "manga-ocr==0.1.10",
        "numpy==1.26.3",
        "opencv-python==4.9.0.80",
        "torch==2.2.0",
        "transformers==4.37.2",
        "pydantic==2.5.3"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Topic :: Education :: Language Learning"
    ],
    python_requires=">=3.10",
) 