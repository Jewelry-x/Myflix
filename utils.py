import shutil
from config import NEO4J_IP

def get_external_ip():
    if NEO4J_IP == 'localhost':
        return 'localhost'
    else:
        shutil.copyfile('../external_config.py', 'repo/external_config.py')
        try:
            from external_config import EXTERNAL_IP

            return EXTERNAL_IP
        except ImportError:
            pass
                    