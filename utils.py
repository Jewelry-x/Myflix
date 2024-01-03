import subprocess
import json
from config import NEO4J_IP

def get_external_ip():
    if NEO4J_IP == 'localhost':
        return 'localhost'
    else:
        try:
            # Run the 'gcloud' command to get the external IP address
            result = subprocess.run(
                ['gcloud', 'compute', 'instances', 'describe', 'your-instance-name', '--zone', 'your-instance-zone', '--format', 'json'],
                stdout=subprocess.PIPE,
                check=True
            )

            # Parse the JSON output and retrieve the external IP address
            instance_info = json.loads(result.stdout)
            external_ip = instance_info['networkInterfaces'][0]['accessConfigs'][0]['natIP']
            
            return external_ip
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving external IP: {e}")
            return None