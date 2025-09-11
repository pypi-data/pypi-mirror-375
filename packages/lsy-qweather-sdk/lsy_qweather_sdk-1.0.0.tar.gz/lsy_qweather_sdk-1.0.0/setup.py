from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="lsy-qweather-sdk",
    version="1.0.0",
    author="fhp",
    author_email="chinafengheping@outlook.com",
    description="和风天气开发服务Python接口（https://dev.qweather.com）",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/9kl/py-qweather",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=["requests>=2.25.0"],
)
