from setuptools import setup, find_packages
  
setup(
    name='AutoSurvey',
    version='0.1',
    description='AutoSurvey is a package for generating surveys.',
    author='T and T',
    author_email='place@holder.com',
    packages=find_packages(include=['AutoSurvey', 'AutoSurvey.*']),
    install_requires=[
        'openai',
    ],
)