import setuptools

setuptools.setup(
	name="gandan", # Replace with your own username
	version="0.4.0",
	author="SANG-HUN, KIM",
	author_email="fury8208@gmail.com",
	description="a small tcp based middlware for raw with advanced pub-sub features",
    long_description="a small tcp based middlware for raw with advanced pub-sub features including publisher callbacks, subscription intervals, and data optimization",
    long_description_content_type='text/markdown',
	url="https://github.com/willcaster0418/gandan",
	packages=["gandan"],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	]
)
