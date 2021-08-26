import sys
import subprocess


def install():
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'python_dependencies.txt'])
    except Exception as e:
        raise Exception(f'Failed to install package. Exception [{str(e)}]')
