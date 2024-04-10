#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 12:17:17 2023

@author: simon
"""
import os
import pyminizip
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm
import json
import warnings

from tools import choose_folder, get_mprage_nifti, convert_dicom_to_nifti
from tools import check_create_folder, share_file_with_password
from tools import random_password, upload_file_to_nextcloud

def get_credentials(path):
    with open(path, 'r') as f:
        creds = json.load(f)
    if creds['username']=='nextcloud_user' or creds['password']=='nextcloud_password':
        warnings.warn('please set user/password in credentials.json')
    if creds['nextcloud_baseurl']=='https://cloud.server.de':
        warnings.warn('please set server in credentials.json')
    return creds

    
def calculate_expire_date(days=14):
    today = datetime.now()
    future_date = today + timedelta(days=days)  # Approximating a month as 30 days
    return future_date.strftime('%Y-%m-%d')

if __name__=='__main__':

    
    creds = get_credentials('./credentials.json')
    
    baseurl      = creds['nextcloud_baseurl']
    username     = creds['username']
    password     = creds['password']
    remote_path  = creds['remote_path']
    inc_mricron  = creds['include_mricron']
    expire_days  = creds['expiration_days']

    # check if MRICron is available

    if inc_mricron:
        mricron_exe = os.path.abspath('./mricron.exe')
        assert os.path.isfile(mricron_exe)
        
    # check that remote folder exists and if not, create it
    check_create_folder(username, password, baseurl, remote_path)
    
    # Step 1: Choose folder and convert to NIFTI
    main_folder = choose_folder(title='Choose a folder that contains MRI folders with DICOM files')
    assert main_folder, 'No folder selected'
    sub_folders = sorted([sub for f in os.listdir(main_folder) if os.path.isdir(sub:=os.path.join(main_folder, f))])

    # Zip the files with the password
    xlsx = os.path.abspath(os.path.join(main_folder, 'share-list.xlsx'))
    if not os.path.isfile(xlsx):
        print('creating new share-list.xlsx')
        df = pd.DataFrame(columns=['url', 'password', 'expire'])
    else:
        print('loading previously existing share-list.xlsx')
        df = pd.read_excel(xlsx, index_col=0)

    for folder in tqdm(sub_folders, desc='subjects'):
        subj = os.path.basename(folder)
        
        if subj in df.index:
            print(f'[{subj}] already shared')
            continue
        
        # convert DICOM to NIFTI
        mprage = get_mprage_nifti(folder)
        if not mprage:
            print(f'[{subj}] converting DICOM to NIFTI')

            convert_dicom_to_nifti(folder)
            mprage = get_mprage_nifti(folder)
            if len(mprage)==0:
                raise Exception(f'[{subj}] conversion of {subj} failed, no mprage found')
     
        assert (filesize:=os.path.getsize(mprage))>6*1024**2, f'[{subj}] file too small {filesize=}'

        # create a random, non-reproducible password
        share_password = random_password()

        # zip the MRI together with the executable and the ini file
        print(f'[{subj}] compressing')
        output_zip = f'{folder}/{subj}.zip'
        ini_file = './mricron.ini'
        with open(ini_file, 'w') as f:
            string = f'[MRU]\nfile0=.\{os.path.basename(mprage)}'
            f.write(string)
            

        files = [mprage] + ([mricron_exe, ini_file] if inc_mricron else [])
        pyminizip.compress_multiple(files, [], output_zip, share_password, 0)

        # upload to nextcloud
        print(f'[{subj}] uploading')
        remote_file_path = f'{remote_path}/{subj}.zip'

        res = upload_file_to_nextcloud(username, password, output_zip, baseurl, remote_file_path)
        assert res=='File uploaded successfully'

        # now share the file with password and expiry
        print(f'[{subj}] getting url')


        expire = calculate_expire_date(days=expire_days)
        res = share_file_with_password(username, password, remote_file_path, share_password, expire, baseurl)
        assert not 'Error: ' in res
        sharing_url = (res.split('<url>')[1]).split('</url>')[0]

        df.loc[subj] = [sharing_url, share_password, expire]
        df.to_excel(xlsx)

print(f'##########################\nlinks and passwords saved to {xlsx}')
