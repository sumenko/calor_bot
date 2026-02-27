allowed_commands = {
    'td' : "transmission-remote 192.168.10.121 -n transmission:transmission -l | grep 'Done' |awk -F'  +' 'NR>1 { print $NF }'", 
    'a': 'uname'}