from setuptools import setup, find_packages

setup(
   name='meu-investimento-thiagonespereira',
   version='0.1',
   packages=find_packages(),
   install_requires=[],
   author='Thiago L Pereira',
   author_email='tlpereir@gmail.com',
   description='Uma biblioteca para cálculos de investimentos.',
   url='https://github.com/thiagonespereira/meu_investimento',
   classifiers=[
       'Programming Language :: Python :: 3',
       'License :: OSI Approved :: MIT License',
       'Operating System :: OS Independent',
   ],
   python_requires='>=3.6',
)