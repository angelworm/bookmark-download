from setuptools import setup

try:
    import py2exe
except:
    pass

setup(name='dlb',
      version = '1.0',
      py_modules = ['dlb'],
      install_requires = [
          'mechanize',
          'lxml',
          'requests'
      ],
      package_dir={'dlb': 'dlb'},
      packages=['dlb'],
      console=['dlb/main.py'],
      entry_points = {
        'console_scripts': ['dlb=dlb.main:main'],
    }

)
