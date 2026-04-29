from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='venta-protocol-v2-device',
    version='0.1.0',
    description='Control Venta Air Humidifiers that use Protocol Version 2',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/tonyjurg/venta_protocol_v2_device',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    packages=['venta_protocol_v2_device'],
    include_package_data=True,
    install_requires=['requests'],
)
