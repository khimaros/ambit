import glob
import os
import pathlib
import setuptools

package_data=dict()
package_data['ambit'] = []
for path, paths, files in os.walk('ambit/resources/', followlinks=True):
    for f in files:
        include = os.path.join(path, f)[6:]
        package_data['ambit'].append(include)

setuptools.setup(
    name='ambit',
    version='0.3.5',
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
    package_data=package_data,
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

