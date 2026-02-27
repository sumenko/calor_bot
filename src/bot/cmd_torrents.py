import subprocess
from commands import allowed_commands

# Example: ping a host and use grep and awk to extract the success count
# shell_command = "ping 1.1.1.1 -c 1 | grep 'received' | awk -F',' '{ print $2}' | awk '{ print $1}'"
shell_command = allowed_commands['a']
try:
    result = subprocess.run(shell_command, shell=True, capture_output=True, text=True, check=True)
    print(f"Received count: {result.stdout.strip()}")
except subprocess.CalledProcessError as e:
    print(f"Command failed: {e.stderr}")