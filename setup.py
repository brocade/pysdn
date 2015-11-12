import versioneer
from setuptools import setup
import pysdn

setup(
    name='pysdn',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='A Python library for programming your network via the Brocade SDN Controller (BSC)',
    long_description=open('README.rst').read(),
    author='Brocade Communications',
    author_email='tnadeau@brocade.com',
    url='https://github.com/brocade/pysdn',
    packages=['pysdn',
              'pysdn.common',
              'pysdn.controller',
              'pysdn.netconfdev',
              'pysdn.netconfdev.vrouter',
              'pysdn.netconfdev.ovs',
              'pysdn.netconfdev.vdx',
              'pysdn.openflowdev'
              ],
    install_requires=['requests>=1.0.0',
                      'PyYAML',
                      'xmltodict'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    license='Brocade Communications, Inc.',
    keywords='sdn nfv bvc brocade sdn controller network vrouter',
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
