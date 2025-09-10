from setuptools import setup, find_packages

setup(name="qyrusai",
      version="1.0.0",
      author="Qyrus Inc",
      author_email="support@qyrus.com",
      description="Qyrus AI SDK",
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown",
      url="",
      packages=find_packages(),
      install_requires=["httpx==0.25.0", "pydantic==2.4.2", "fastapi==0.111.0"],
      python_requires=">=3.7")
