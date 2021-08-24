import sys
import subprocess


class Package:
    REQUIRED_PACKAGE = ["jsonschema", "requests", "boto3"]

    def install(self):
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', *Package.REQUIRED_PACKAGE], stdout=subprocess.DEVNULL)
        except Exception as e:
            raise Exception(f'Failed to install package. Exception [{str(e)}]')
