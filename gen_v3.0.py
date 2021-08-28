import os
from pathlib import Path
import zipfile
import sys
from subprocess import call
import subprocess
import shutil
from shutil import rmtree
import requests
import git


def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()

    response = session.get(URL, params = { 'id' : id }, stream = True)
    token = get_confirm_token(response)

    if token:
        params = { 'id' : id, 'confirm' : token }
        response = session.get(URL, params = params, stream = True)

    save_response_content(response, destination)    

def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value

    return None

def save_response_content(response, destination):
    CHUNK_SIZE = 32768

    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)


def zip_extract(zipname):
    password = None
    # open and extract all files in the zip
    z = zipfile.ZipFile(zipname, "r")
    z.extractall(pwd=password)
    z.close()


def edit_req(route):
    
    sql_libraries = {'1' : 'Flask-SQLAlchemy', '2' : 'PyMySQL', '3' : 'SQLAlchemy'}
    libraries = {'1' : 'Jinja2', '2' : 'itsdangerous', '3' : 'Werkzeug', '4' : 'flask_wtf', '5' : 'flask_login', '6' : 'python-dotenv'}

    anssql = input('install SQL libraries? y/n:\t') 
    if anssql.lower() == 'y':
        f = open('%s/requirements.txt' % route,'a')
        for key, value in sql_libraries.items():
            f.write('%s\n' % (value))
        f.close()

    for key, value in libraries.items():
        ans = input('you require %s in your project? y/n:\t' % value)
        if ans.lower() == 'y':
            f = open('%s/requirements.txt' % route,'a')
            f.write('%s\n' % (value))
            f.close()
    

def env(route):
    
    os.chdir(route)
    os.system('chmod 555 ./install.sh')
    subprocess.call("./install.sh", shell=True)


def repo_builder(route):
    
    URL = input('Enter URL of the project repository:\t')
    path_directory = os.getcwd()
    os.chdir(path_directory)
    # git init new_repo
    new_repo = git.Repo.init()
    repo = git.Repo()

    # Create a new remote
    try:
        repo.create_remote('origin', URL)
    except git.exc.GitCommandError as error:
        print(f'Error creating remote: {error}')

    os.system('git pull --allow-unrelated-histories origin master')
    os.system('git add .')
    os.system('git commit -m "initial commit"')
    os.system('git push origin master')
    

def main():
    
    struct_opt = int(input('\nEnter the number of the desired structure\n 1.Functional\n 2.MVC (Model, View, Controller)\n'))

    if struct_opt == 1:
        struct_name = 'functional'
        zip_name = 'functional.zip'
        struct_id = '1GWyNuJOyTR12EW_k6RIuT949Hgjztamg'
    elif struct_opt == 2:
        struct_name = 'MVC'
        zip_name = 'MVC.zip'
        struct_id = '1zbVMzsIlbx5LzidM46LUGVaXWJkZmwo0'


    file_id = str(struct_id)
    destination = str(zip_name)
    download_file_from_google_drive(file_id, destination)
   
    zip_extract(zip_name)
    
    project_name = input('Ingres project name:\t')
    if os.path.isdir(project_name):
        repans = input('folder already exist, replace? y/n\t')
        if repans.lower() == 'y':
            shutil.rmtree(project_name)
            os.rename(struct_name, project_name)
        else:
            sys.exit(0)
    else:
        os.rename(struct_name, project_name)

    path = Path("%s/app" % project_name)
    edit_req(path)
    env(path)
    repo_builder(path)


if __name__ == '__main__':
    main()
