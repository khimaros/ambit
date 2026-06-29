import glob
import os
import setuptools

# project metadata and dependencies live in pyproject.toml. only the
# dynamic package_data walk and bin/ script discovery remain here.

package_data = {'ambit': []}
for path, _, files in os.walk('ambit/resources/', followlinks=True):
    for f in files:
        package_data['ambit'].append(os.path.join(path, f)[6:])

setuptools.setup(
    package_data=package_data,
    scripts=glob.glob('./bin/*'),
)
