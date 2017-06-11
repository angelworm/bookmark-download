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
          'requests',
      ],
      options = {
          "py2exe": {
              'packages': [
                  'lxml.etree',
                  'lxml._elementpath',
                  'urllib2',
                  'gzip',
              ],  
              
          }
      },
      zipfile=None,
      package_dir = {'dlb': 'dlb'},
      packages=[
          'dlb',
      ],
      console=['run.py'],
      entry_points = {
        'console_scripts': ['dlb=dlb.dlb:main'],
    }

)
