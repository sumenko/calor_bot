import subprocess
from dotenv import load_dotenv
import os
from cut_tags import TagsContainer
from mock_data import td_mock
import sys

load_dotenv()  # Загружаем переменные из .env
DEBUG = os.getenv("DEBUG")


def command_execute_os(command, message):
    if DEBUG =='1':
        return allowed_commands[command]['mock']
    try:
        return subprocess.run(allowed_commands[command]['arg_text'], shell=True, capture_output=True, text=True, check=True).stdout.strip()
    except subprocess.CalledProcessError as e:
        return f'Error: {e}'



def command_add_remove_tag(command, message):
    if command == 'addtg' or command == 'rmtg':
        tc = TagsContainer()
        tag = message.split(command)[-1].strip()
        if command == 'addtg':
            tc.add_tag(tag, flush=True)
            return f'add tag \'{tag}\''

        if command == 'rmtg':
            tc.rm_tag(tag, flush=True)
            return f'remove tag \'{tag}\''
        
    return 'error'

def command_halt(command, message):
    return sys.exit(0)

def command_list_commands(command, message):
    return '\n'.join([' - '.join(('/' + k, allowed_commands[k]['help'])) for k in allowed_commands])


allowed_commands = {
    'td' : 
        {'arg_text': "transmission-remote 192.168.10.121 -n transmission:transmission -l | grep 'Done' |awk -F'  +' 'NR>1 { print $NF }'", 
         'func' : command_execute_os,
         'mock' : td_mock,
         'help' : 'List downloaded files from transmission daemon'
         }, 
    'a': {
        'arg_text': 'uname -a',
        'func': command_execute_os,
        'mock' : 'Linuxxxx',
        'help' : 'OS info' 
        },
    'la': {
        'arg_text': 'ls -a',
        'func': command_execute_os,
        'mock' : 'list files',
        'help' : 'OS info',
        },
    'addtg' : {
        'arg_text': '',
        'func': command_add_remove_tag,
        'mock' : 'add_tag',
        'help' : 'add tag to filter for file names',
        },
    'rmtg' : {
        'arg_text': '',
        'func': command_add_remove_tag,
        'mock' : 'rm_tag',
        'help' : 'remove tag to filter for file names',
        },
    'halt' : {
        'arg_text': '',
        'func': command_halt,
        'mock' : 'exit(0)',
        'help' : 'stop bot',
        },
    'help' : {
        'arg_text': '',
        'func' : command_list_commands,
        'mock' : 'help',
        'help' : 'list of commands'
       },
    }


if __name__ == '__main__':
    command = 'atg'
    message = 'atg ttt'
    # print(allowed_commands[command]['func'](command, message))
    a = command_list_commands('', '')
    print(a)