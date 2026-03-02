import subprocess
from dotenv import load_dotenv
import os
from cut_tags import TagsContainer
from cut_tags import TorrentFileNameCleaner
from mock_data import td_mock
import sys

load_dotenv()  # Загружаем переменные из .env
DEBUG = os.getenv("DEBUG")


def command_execute_os(command, message, arg=''):
    cmd = allowed_commands[command]['arg_text'] + ' ' + arg
    if DEBUG =='1':
        return allowed_commands[command]['mock'], cmd
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True).stdout.strip(), cmd
    except subprocess.CalledProcessError as e:
        return f'Error: {e}', cmd

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

def command_ls_downloads(command, message):
    result = command_execute_os(command, message).encode('windows-1251').decode('utf8')
    if not 'error' in result.lower():
        print(result)
        tfc = TorrentFileNameCleaner()
        return tfc.get_clean_numbered_text(result)
    else:
        return 'no torrents'


def command_torrent(command, message):
    return 'added'

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
    'dls' : 
        {'arg_text': "ls downloads/*.torrent", 
         'func' : command_ls_downloads,
         'mock' : 'dls mock!!!',
         'help' : 'List downloads dir'
         },
    'add' : 
        {'arg_text': "transmission-remote 192.168.10.121 -n transmission:transmission -a", 
         'func' : command_torrent,
         'mock' : 'mock!!!',
         'help' : 'Usage: add <Movies> | <Serials> | <Cartoon> add torrents to specific folder'
         },

    'a': {
        'arg_text': 'uname -a',
        'func': command_execute_os,
        'mock' : 'Linuxxxx',
        'help' : 'OS info' 
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
    command = 'dls'
    message = 'dls ttt'
    print(allowed_commands[command]['func'](command, message))
    