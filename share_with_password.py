#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refactored script for sharing BIDS-formatted anatomical NIfTI scans via Nextcloud.

@author: basis by Simon Kern, added BIDS functionality by Lea Wazulin
"""

import sys


import os
import pyminizip
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
import json
import warnings

from tools import choose_folder, check_create_folder, share_file_with_password
from tools import random_password, upload_file_to_nextcloud

def get_credentials(path):
    with open(path, 'r') as f:
        creds = json.load(f)
    if creds['username'] == 'nextcloud_user' or creds['password'] == 'nextcloud_password':
        warnings.warn('Please set username/password in credentials.json')
    if creds['nextcloud_baseurl'] == 'https://cloud.server.de':
        warnings.warn('Please set server URL in credentials.json')
    return creds

def calculate_expire_date(days=14):
    today = datetime.now()
    future_date = today + timedelta(days=days)
    return future_date.strftime('%Y-%m-%d')

def find_t1w_nii(folder):
    anat_folder = os.path.join(folder, 'anat')
    if not os.path.isdir(anat_folder):
        return None
    for file in os.listdir(anat_folder):
        if file.endswith('_T1w.nii.gz'):
            return os.path.join(anat_folder, file)
    return None

if __name__ == '__main__':

    creds = get_credentials('./credentials.json')

    baseurl      = creds['nextcloud_baseurl']
    username     = creds['username']
    password     = creds['password']
    remote_path  = creds['remote_path']
    inc_mricron  = creds['include_mricron']
    expire_days  = creds['expiration_days']

    if inc_mricron:
        mricron_exe = os.path.abspath('./mricron.exe')
        assert os.path.isfile(mricron_exe), 'mricron.exe not found'

    check_create_folder(username, password, baseurl, remote_path)

    main_folder = choose_folder(title='Choose BIDS dataset root folder')
    assert main_folder, 'No folder selected'

    sub_folders = sorted([
        os.path.join(main_folder, f)
        for f in os.listdir(main_folder)
        if os.path.isdir(os.path.join(main_folder, f)) and f.startswith('sub-')
    ])

    xlsx = os.path.abspath(os.path.join(main_folder, 'share-list.xlsx'))
    if not os.path.isfile(xlsx):
        print('Creating new share-list.xlsx')
        df = pd.DataFrame(columns=['url', 'password', 'expire'])
    else:
        print('Loading existing share-list.xlsx')
        df = pd.read_excel(xlsx, index_col=0)

    for folder in tqdm(sub_folders, desc='Subjects'):
        subj = os.path.basename(folder)

        if subj in df.index:
            print(f'[{subj}] already shared')
            continue

        t1w_file = find_t1w_nii(folder)
        if not t1w_file or not os.path.isfile(t1w_file):
            print(f'[{subj}] No T1w NIfTI found, skipping...')
            continue

        filesize = os.path.getsize(t1w_file)
        assert filesize > 6 * 1024**2, f'[{subj}] file too small ({filesize} bytes)'

        share_password = 'ZI-J5-' + random_password(5, nwords=2)

        print(f'[{subj}] Compressing')
        output_zip = os.path.join(folder, f'{subj}.zip')

        ini_file = os.path.join(folder, 'mricron.ini')
        with open(ini_file, 'w') as f:
            string = f'[MRU]\nfile0=./{os.path.basename(t1w_file)}'
            f.write(string)

        files_to_zip = [t1w_file] + ([mricron_exe, ini_file] if inc_mricron else [])
        pyminizip.compress_multiple(files_to_zip, [], output_zip, share_password, 0)

        print(f'[{subj}] Uploading')
        remote_file_path = f'{remote_path}/{subj}.zip'
        res = upload_file_to_nextcloud(username, password, output_zip, baseurl, remote_file_path)
        assert res == 'File uploaded successfully', f'[{subj}] Upload failed: {res}'

        print(f'[{subj}] Getting sharing URL')
        expire = calculate_expire_date(days=expire_days)
        res = share_file_with_password(username, password, remote_file_path, share_password, expire, baseurl)
        assert not 'Error: ' in res, f'[{subj}] Sharing failed: {res}'

        sharing_url = (res.split('<url>')[1]).split('</url>')[0]
        df.loc[subj] = [sharing_url, share_password, expire]
        
        os.remove(output_zip)
        os.remove(ini_file)
        
print("\nPlease choose a folder to save the share-list.xlsx file:")
sharelist_folder = choose_folder(title='Select folder to save share-list.xlsx')

if sharelist_folder:
    xlsx_out_path = os.path.join(sharelist_folder, 'share-list.xlsx')
    df.to_excel(xlsx_out_path)
    print(f'\n#############################\nLinks and passwords saved to {xlsx_out_path}')
else:
    print('\nNo folder selected. The share list was not saved.')

    
 
