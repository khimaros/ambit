import setuptools

setuptools.setup(
    name='ambit',
    version='0.1',
    description='Take control of your Palette.',
    url='https://github.com/khimaros/ambit',
    author='khimaros',
    packages=['ambit'],
    scripts=[
        'bin/ambit',
        'bin/ambit_gui',
        'bin/ambit_simulator',
        'bin/ambit_image_convert',
        'bin/ambit_image_display',
        'bin/ambit_push_assets',
        'bin/ambit_map_midi',
        'bin/ambit_map_hid',
        'bin/ambit_demoscene',
        'bin/ambit_demoscene_simulator',
        'bin/ambit_lavalamp',
        'bin/ambit_lavalamp_simulator',
        'bin/ambit_lightshow',
        'bin/ambit_lightshow_gui',
        'bin/ambit_lightshow_simulator',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Topic :: System :: Hardware',
    ],
    python_requires='>=3.6',
)
