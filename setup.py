from setuptools import setup
import pybvc

setup(
    name='pybvc',
    version=pybvc.__version__,
    description='A python library for programming your network via the Brocade Vyatta Controller (BVC)',
    long_description=open('README.rst').read(),
    author='Elbrys Networks',
    author_email='jeb@elbrys.com',
    url='https://github.com/brcdcomm/pybvc',
    packages=['pybvc',
              'pybvc.common',
              'pybvc.controller',
              'pybvc.netconfdev',
              'pybvc.netconfdev.vrouter',
              'pybvc.netconfdev.vdx',
              'pybvc.openflowdev'
              ],
    install_requires=['requests>=1.0.0',
                      'PyYAML',
                      'xmltodict'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    license='BSD',
    keywords='sdn nfv bvc brocade vyatta controller network vrouter',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)
