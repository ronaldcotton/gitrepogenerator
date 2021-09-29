#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO: only works/validated for python/windows enviornment

import subprocess
import os
import sys
import time
import random
import names
import requests
import zlib
import argparse
import platform

dbug = True

# see https://stackoverflow.com/a/12117089/6125870
class Range(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end
    def __eq__(self, other):
        return self.start <= other <= self.end


def program_args():
    parse = argparse.ArgumentParser(description='Git Repo Generator')

    parse.add_argument('-t', '--task', type = int, default = 1, help = 'Enter number of tasks to complete')
    parse.add_argument('-l','--length', type = int, default = 40, choices=[Range(2,10000)], help = 'Max Length of history')
    parse.add_argument('-d','--depth', type = int, default = 1, choices=[Range(1,20)], help = 'Max depth of branches')
    parse.add_argument('-b','--branch', type = int, default = 1, help = 'Max Number of branches')
    parse.add_argument('-u','--unmerged', type = int, default = 1, help = 'Max Number of non-merged branches')
    parse.add_argument('-n','--num', type = int, default = 10, help = 'Number of Users')
    parse.add_argument('-p','--probability', type = float, choices=[Range(0.0, 1.0)], default = .15 , help = 'probability of branch')
    return vars(parse.parse_args())


def line_feed():
    return '\n'  # placed here in case you need to change to \r\n

def time_hash():
    return hash(time.time())


def clean_line(line):
    return line.decode('utf-8').replace('\r','').replace('\n','')


def command(cmd):
    global dbug
    cmdlist = cmd.split()
    cmdlist[-1] = cmdlist[-1].replace('_',' ')
    stdout = []
    stderr = []
    process = subprocess.Popen(cmdlist, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for oline in process.stdout:
        stdout.append(clean_line(oline))
    for eline in process.stderr:
        stderr.append(clean_line(eline))
    errcode = process.returncode
    if dbug:
        print(f'cmd: {cmd} stdout: {stdout} stderr: {stderr} errcode: {errcode}')
    return  stderr, stdout


def random_domain(dictionary):
    num_of_dictionary = random.randint(1,3)
    domain_name = ''
    for i in range(num_of_dictionary):
        domain_name += dictionary[random.randint(0, len(dictionary))]
    return domain_name


def random_email(dictionary):
    characters = 'abcdefghijklmnopqrstuvwxyz'
    domain = random_domain(dictionary)
    name = names.get_full_name()
    subdomain = ''
    if random.choice([True, False]):
        for n in range(random.randint(2,5)):
            subdomain += characters[random.randint(0,len(characters)-1)]
    emailname = name.lower().replace(' ', '')
    if random.choice([True, False]):
        emailname += str(random.randint(1,99))
    if subdomain:
        email = emailname + '@' + subdomain + '.' + domain + random.choice(['.com', '.org', '.net','.edu', '.gov',])
    else:
        email = emailname + '@' + domain + random.choice(['.com', '.org', '.net', '.edu', '.gov', '.mil'])
    return name, email


def init_repo(hash):
    command(f'mkdir repo-{hash}')
    os.chdir(f'./repo-{hash}')
    print(os.getcwd())
    command('git init')
    #command('git config init.defaultBranch main')  # becoming the standard - TODO
    
    
def commit_repo(filename, number, note=None):
    if note != 'delete':
        if '.' in filename: 
            command(f'git add {filename}')
        else:
            command(f'git add ./{filename}/readme.txt')
    if note == None:
        command(f'git commit -m "{filename}_-_commit_{number}"')
    else:
        command(f'git commit -m "{note}_{filename}_-_commit_{number}"')


def change_user_repo(name, email):
    command(f'git config user.name "{name}"')
    command(f'git config user.email "{email}"')


def add_new_file_repo_user(name, email, files, dictionary):
    change_user_repo(name, email)

    newfile = False
    while not newfile:
        f = random_file(dictionary)
        if f not in files:
            files.append(f)
            command(f'type nul > {f}') # touch in linux
            for i in range(1, random.randint(2,20)):
                command(f'echo Line{i} >> {f}')
            newfile = True
    return f


def remove_from_repo(name, email, files_or_folders, filename):
    change_user_repo(name, email)

    files_or_folders.remove(filename)
    command(f'git rm -r {filename}')

    return filename

def add_new_folder_repo_user(name, email, folders, dictionary):
    change_user_repo(name, email)

    newfolder = False
    while not newfolder:
        f = random_folder(dictionary)
        if f not in folders:
            folders.append(f)
            command(f'mkdir {f}')
            newfolder = True
            efile = open(f'./{f}/readme.txt', "w")
            efile.write(f'placeholder {line_feed()}')
            efile.close()
    return f

def edit_files_repo(name, email, filename):
    change_user_repo(name, email)

    efile = open(filename, 'r')
    lines = efile.readlines()

    change_line = random.randint(0, len(lines)-1)

    lines[change_line] = f'Line{change_line+1} changed.' + line_feed()

    efile = open(filename, "w")
    efile.writelines(lines)
    efile.close()
    return filename

def rename_file_or_folder_repo(name, email, files_or_folders, filename):
    change_user_repo(name, email)
    
    files_or_folders.remove(filename)

    newfile = False
    while not newfile:
        if '.' in filename:
            f = random_file(dictionary)
        else:
            f = random_folder(dictionary)
        if f not in files_or_folders:
            files_or_folders.append(f)
            command(f'git mv {filename} {f}')
            return f


def continue_file_repo(name, email, filename):
    change_user_repo(name, email)

    efile = open(filename, 'r')
    lines = efile.readlines()

    linecount = len(lines) + 1
    lines = []
    for i in range(random.randint(1,20)):
        lines.append(f'Line{linecount}' + line_feed())
        linecount += 1

    efile = open(filename, "a")
    efile.writelines(lines)
    efile.close()
    return filename


def keyword_file_repo(name, email, randomuser, keywordlist, filename, dictionary):
    if keywordlist[randomuser] == None:
        keywordlist[randomuser] = dictionary[random.randint(0, len(dictionary))]

    efile = open(filename, 'r')
    lines = efile.readlines()

    linecount = len(lines) + 1
    lines = []
    lines.append(f'Line{linecount} keyword {keywordlist[randomuser]}' + line_feed())

    efile = open(filename, "a")
    efile.writelines(lines)
    efile.close() 
    return filename

def random_file(dictionary):  # all files MUST have extensions for some logic to work
    extension = ['txt', 'md', '1st', 'log', 'html', 'css', 'c', 'cpp', 'h', 'hpp', 'py', 'json', 'xml', 'csv', 'js', 'sh']
    basefilename = ['readme', 'file', 'output', 'about', 'home', 'example', 'edit', 'home']

    if random.choice([True, False]):
        f = basefilename[random.randint(0, len(basefilename)-1)] + '.' + extension[random.randint(0, len(basefilename)-1)]
    else:
        if random.choice([True, False]):
            f = basefilename[random.randint(0, len(basefilename)-1)] + '-' + str(time_hash()) + '.' + extension[random.randint(0, len(extension)-1)]
        else:
            random_word = ''
            while len(random_word) < 3:
                random_word = dictionary[random.randint(0, len(dictionary)-1)]
            f  = random_word + '.' + extension[random.randint(0, len(basefilename)-1)]
    return f 


def random_folder(dictionary):
    basefoldername = ['bin', 'src', 'tmp', 'temp', 'build', 'docs', 'documents', 'test', 'tools', 'dep', 'inc', 'lib', 'tools', 'scripts']
    random_word = ''

    if random.choice([True, False]):
        return basefoldername[random.randint(0, len(basefoldername)-1)] + '-' + str(time_hash())
    else:
        while len(random_word) < 3:
            random_word = dictionary[random.randint(0, len(dictionary)-1)]
        return random_word


def dl_save_dict():
    word_site = 'https://www.mit.edu/~ecprice/wordlist.10000'

    response = requests.get(word_site)
    dictionary = response.content

    with open('dictionary.zlib', 'wb') as txtfile:
        txtfile.write(zlib.compress(dictionary))
    
    return dictionary.decode('utf-8').splitlines()


def unzip_dict():
    return (zlib.decompress(open('dictionary.zlib', 'rb').read())).decode('utf-8').splitlines()


def repo_actions(name, email, randomuser, keywordlist, files, folders, dictionary):
    actioncomplete = False
    while not actioncomplete:
        # increasing chances of edit, continue, and keyword
        action = random.choice(['new', 'delete', 'edit', 'edit', 'edit', 'rename', 'continue', 'continue', 'continue', 'continue', 'keyword', 'keyword'])
        randomuser = random.randint(0,len(name)-1)
        if action == 'new':
            if random.choice([True, False]):
                f = add_new_file_repo_user(name[randomuser], email[randomuser], files, dictionary)
            else:
                f = add_new_folder_repo_user(name[randomuser], email[randomuser], folders, dictionary)
            actioncomplete = True
        elif action == 'delete':
            if files == [] and folders == []:
                continue
            if random.uniform(0,1) > .10:
                continue
            else:
                if files != []:
                    f = remove_from_repo(name[randomuser], email[randomuser], files, random.choice(files))
                else:
                    f = remove_from_repo(name[randomuser], email[randomuser], folders, random.choice(folders))
            actioncomplete = True
        elif action == 'edit':
            if files == []:
                continue
            else:
                f = edit_files_repo(name[randomuser], email[randomuser], random.choice(files))
        elif action == 'rename':
            if files == [] and folders == []:
                continue
            else:
                if files != []:
                    f = rename_file_or_folder_repo(name[randomuser], email[randomuser], files, random.choice(files))
                else:
                    f = rename_file_or_folder_repo(name[randomuser], email[randomuser], folders, random.choice(folders))
            actioncomplete = True
        elif action == 'continue':
            if files == []:
                continue
            else:
                f = continue_file_repo(name[randomuser], email[randomuser], random.choice(files))
            actioncomplete = True
        elif action == 'keyword':
            if files == []:
                continue
            else:
                f = keyword_file_repo(name[randomuser], email[randomuser], randomuser, keywordlist, random.choice(files), dictionary)
            actioncomplete = True
        else: # added actions -- unknown behavior
            print('ERROR: unknown action -- nothing to do.')
            continue
    return f, action


if __name__ == "__main__":
    args = program_args()
    currtimehash = time_hash()
    basepath = os.getcwd() # will be used later for nested folders
    branchnum = 1

    if not os.path.exists('dictionary.zlib'):
        dictionary = dl_save_dict()
    else:
        dictionary = unzip_dict()

    init_repo(currtimehash)

    name = [] # not using dictionary incase random name comes up twice...
    email = []
    for i in range(args['num']):
        n, e = random_email(dictionary)
        name.append(n)
        email.append(e)
    keywordlist = [None] * args['num']
    
    # TODO: Let's not program tasks until we have the repo design working and we can have a way
    # to verify the tasks... Also, tasks MUST be completed in the order that they were made.
    # also, need to know where to reset the reflog (git reflog; git reset HEAD@{X}) and
    # if user changes that, let user know that there's no way to fix that. lol.

    files = {}
    files['master'] = []
    folders = {}
    folders['master'] = []
    
    # create initial commit - pick random user and add one file and/or one folder - check if branch is required
    # TODO: nested folders, for the moment, no nested folders to reduce complexity.

    randomuser = random.randint(0,len(name)-1)
    if random.choice([True, False]):
        f = add_new_file_repo_user(name[randomuser], email[randomuser], files['master'], dictionary)
    else:
        f = add_new_folder_repo_user(name[randomuser], email[randomuser], folders['master'], dictionary)
    
    commitnum = 1
    branchnum = 0
    commit_repo(f, commitnum, 'init_added')

    args['length'] -= 1

    # create additional commits - check to see branch
    for l in range(args['length']):
        commitnum += 1
        command(f'git checkout master')
        f, action = repo_actions(name, email, randomuser, keywordlist, files['master'], folders['master'], dictionary)
        commit_repo(f, commitnum, action)
        if random.uniform(0,1) < args['probability']:
            branchnum += 1
            branchname = f'branch{branchnum}'
            files[branchname] = []
            folders[branchname] = []
            for m in range(random.randint(1,args['length']//6)):
                commitnum += 1
                command(f'git checkout -b {branchname}')
                f, action = repo_actions(name, email, randomuser, keywordlist, files[branchname], folders[branchname], dictionary)
                commit_repo(f, commitnum, action)
            



    
    