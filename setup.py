import glob
import setuptools

setuptools.setup(
    name='ambit',
    version='0.3.2',
    description='Take control of your Palette.',
    long_description=(
        '**ambit** is a Python library for interacting with PaletteGear '
        'and MonogramCC devices, a graphical simulator for device-free '
        'development, and an accompanying set of configurable end user '
        'tools and demos.'
    ),
    long_description_content_type='text/markdown',
    keywords=['monogramcc', 'palettegear', 'demoscene', 'pygame', 'linux', 'pyusb'],
    url='https://github.com/khimaros/ambit',
    author='khimaros',
    packages=setuptools.find_packages(),
    include_package_data=True,
    scripts=glob.glob('./bin/*'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Topic :: System :: Hardware',
    ],
    python_requires='>=3.6',
)

