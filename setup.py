from setuptools import setup, find_packages
setup(
	name='mml2sympy', 
	version='0.3.0',
	packages=find_packages(exclude=['tests']),
	install_requires=['sympy', 'lxml'],
)
