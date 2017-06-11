from setuptools import setup

setup(name='tool',
      version = '1.0',
      py_modules = ['tool'],
      install_requires = [
          'mechanize',
          'lxml',
          'requests'
      ]
)
