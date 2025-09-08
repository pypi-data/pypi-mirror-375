from setuptools import setup, find_packages

setup(
      name="python-autodiff",
      version="0.1.1",
      author="Om Panchal",
	  author_email="om.panchal2022@gmail.com",
	  maintainer="Om Panchal",
	  maintainer_email="om.panchal2022@gmail.com",
      description="A simple automatic differentiation library",
      long_description=open("README.md").read(),
      long_description_content_type="text/markdown",
      url="https://github.com/OmPanchal/Autodiff",
      packages=find_packages(),
      classifiers=[
          "Programming Language :: Python :: 3",
		  "Topic :: Scientific/Engineering :: Mathematics",
          "License :: OSI Approved :: MIT License",
      ],
	  install_requires=["numpy"],
	  include_dirs=["autodiff"]
  )