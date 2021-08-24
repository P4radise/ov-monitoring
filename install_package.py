import sys
import subprocess
import pkg_resources


class Package:
    REQUIRED_PACKAGE = ["jsonschema", "requests", "boto3"]

    def install(self):
        install_packages = {package.key for package in pkg_resources.working_set}
        missing_packages = []
        for package in Package.REQUIRED_PACKAGE:
            is_package_missing = True
            for install_package in install_packages:
                if package == install_package:
                   is_package_missing = False
                   break

            if is_package_missing is True:
                missing_packages.append(package)

        if missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', *missing_packages], stdout=subprocess.DEVNULL)
            except Exception as e:
                raise Exception(f'Failed to install package - {missing_packages}. Exception [{str(e)}]')
