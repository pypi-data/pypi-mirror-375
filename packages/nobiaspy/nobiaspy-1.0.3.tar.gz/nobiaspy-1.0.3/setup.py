from setuptools import find_packages, setup

setup(
    name="nobiaspy",
    version="1.0.3",
    packages=find_packages(where="./nobiaspy"),
    description="nobiaspy is python cli tool that finds logically fallacies in youtube transcript",
    entry_points={
        "console_scripts": ["nobias=nobiaspy.index:tool"]
    },
    author="jamcha123",
    author_email="jameschambers732@gmail.com"
)