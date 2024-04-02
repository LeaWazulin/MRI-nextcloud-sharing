# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 15:55:49 2024

@author: simon.kern
"""
import os
import random
import requests
import platform
import warnings
from datetime import datetime, timedelta

from tkinter.filedialog import askdirectory
from tkinter import  Tk
import subprocess
from wordfreq import top_n_list

import dicom2nifti
from datetime import datetime, timedelta




def random_password(minlen=5, separator='-'):
    """
    Generate a reproducible random password consisting of three random words
    based on an input string.

    :param input_string: The string used to seed the random number generator, ensuring reproducibility
    :param word_list: The list of words to choose from
    :param separator: The separator to use between words in the password
    :return: A reproducible random password
    """
    wordlist = top_n_list('en', 10000)
    wordlist = [word for word in wordlist if len(word)>minlen and not "'" in word]

    # Choose three random words from the list
    chosen_words = random.sample(wordlist, 3)

    # Create the password by joining the chosen words with the separator
    password = separator.join(chosen_words)

    return password

def check_executable(path):
    """make a script or binary executable"""
    if os.access(path, os.X_OK):
        return True
    mode = os.stat(path).st_mode
    mode |= (mode & 0o444) >> 2    # copy R bits to X
    os.chmod(path, mode)
    return os.access(path, os.X_OK)

def convert_dicom_to_nifti(folder):
    """using dcm2nii, convert folder.  fallback using dicom2nifti package,
       but it's not very reliable"""
    if platform.system().lower() == "windows":
        dcm2nii_binary = './dcm2nii.exe'
    elif platform.system().lower() == "linux":
        dcm2nii_binary = './dcm2nii'
    else:
        warnings.warn('No dcm2nii for MacOS, using dicom2nifti package instead')
        dcm2nii_binary = False

    if dcm2nii_binary:
        try:
            res = subprocess.check_output([dcm2nii_binary, folder])
            convert_success = True

        except Exception as e:
            print(f'cant use dcm2nii, please check error: {repr(e)}')
            convert_success = False

        
    if not convert_success or not dcm2nii_binary:
        # conversion failes, fallback to dicom2nifti

        print('using fallback option dicom2nifti')
        dicom2nifti.convert_directory(folder, folder)

def get_mprage_nifti(folder):
    """return largest nifti in the folder that has MPRAGE in the file name"""
    files = os.listdir(folder)

    nifti = [f for f in files if '.nii' in f]
    mprages = [os.path.join(folder, f) for f in nifti if 'mprage' in f.lower()]

    mprages = sorted(mprages, key=lambda x:os.path.getsize(x))
    if len(mprages)==0: return False
    return mprages[-1]

def choose_folder(default_dir=None,exts='txt', title='Choose file'):
    """
    Open a file chooser dialoge with tkinter.

    :param default_dir: Where to open the dir, if set to None, will start at wdir
    :param exts: A string or list of strings with extensions etc: 'txt' or ['txt','csv']
    :returns: the chosen file
    """
    root = Tk()
    root.iconify()
    root.update()
    if isinstance(exts, str): exts = [exts]
    name = askdirectory(initialdir=None,
                           parent=root,
                           title = title)
    root.update()
    root.destroy()
    if not os.path.exists(name):
        print("No folder chosen")
    else:
        return name

def share_file_with_password(username, password, file_path, share_password, expire, baseurl):
    url = f"{baseurl}/ocs/v2.php/apps/files_sharing/api/v1/shares"

    headers = {
        'OCS-APIRequest': 'true',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    auth = (username, password)
    data = {
        'path': file_path,
        'shareType': 3,  # Public link
        'password': share_password,
        'expireDate': expire
    }

    response = requests.post(url, headers=headers, auth=auth, data=data)

    if response.status_code == 200:
        return response.text  # Or parse the XML response as needed
    else:
        return f"Error: {response.status_code}, {response.text}"

def check_create_folder(username, password, baseurl, remote_path):
    # Set up authentication and headers
    session = requests.Session()
    session.auth = (username, password)
    
    url = f"{baseurl}/remote.php/webdav/{remote_path}"
    print(f'check if {url} exists')
    # Check if folder exists
    check_response = session.request("PROPFIND", url)
    if not 200 <= check_response.status_code < 300:
        # Folder doesn't exist, create it
        create_response = session.request("MKCOL", url)
        if create_response.status_code == 201:
            print(f"Folder {remote_path} created successfully")
        else:
            raise Exception(f'remote folder {remote_path} does not exist and could not be created.')

def upload_file_to_nextcloud(username, password, local_file_path, baseurl, remote_file_path):
    # Construct the full WebDAV URL
    url = f"{baseurl}/remote.php/webdav/{remote_file_path}"

    # Read the file to be uploaded
    with open(local_file_path, 'rb') as file:
        file_contents = file.read()

    # Set up authentication and headers
    auth = (username, password)
    headers = {'Content-Type': 'application/octet-stream'}

    # Send the PUT request to upload the file
    response = requests.put(url, data=file_contents, headers=headers, auth=auth)

    # Check the response status
    if response.status_code in [200, 201, 204]:
        return "File uploaded successfully"
    else:
        return f"Error: {response.status_code}, {response.text}"
