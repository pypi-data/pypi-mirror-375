from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='shifr',
  version='0.0.1',
  author='clown',
  author_email='maxim3hohlov@gmail.com',
  description='',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://pypi.org/manage/projects/',
  packages=find_packages(),
  install_requires=['requests>=2.25.1'],
  classifiers=[
    'Programming Language :: Python :: 3.11',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent'
  ],
  keywords='files shifr_modules ',
  project_urls={},
  python_requires='>=3.6'
)