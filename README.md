# MRI-nextcloud-sharing

According to DGSVO §15, every participant has the right to request data that was recorded about them. That includes research MRIs. If participants makes a requesr on that basis we need a secure way of sharing the sensitive data. 
This repo contains the workshops to share password-protected MRI images via Nextcloud. 
Uploads NIFTI files to Nextcloud zipped with a random password.
You send the link to the NIFTI via mail and the password via a secure second channel e.g. WhatsApp or Signal.

![image](https://github.com/CIMH-Clinical-Psychology/MRI-nextcloud-sharing/assets/14980558/b8e78dc5-2c01-49db-97a7-5de3b46c124f)


## preparation
- clone this repository to your local machine
- install the following via pip:  `pip install dicom2nifti wordfreq tqdm pyminizip`

then enter your credentials into `credentials.json`
```json
   {"username": "username",         # user name for nextcloud
    "password": "password",         # password for the user
    "remote_path": "MRI-share",     # folder on nextcloud in which the files are uploaded.
    "expiration_days": 21,          # delete share after this time
    "include_mricron": true,        # include a program to view NIFTI files (Windows only)
    "nextcloud_baseurl": "https://cloud.server.de"  # server URL
```

## usage

1. run script via `python share_with_password.py` and select the folder that contains the DICOM folders (i.e. the folder above the actual DICOM images, not the folder containing the DICOM images themselves)
2. The script will create random passwords and upload the files to nextcloud
3. A `share-list.xlsx` will be created containing all the links and passwords.
4. If you need to re-share a file, simply delete the row of the participant from the excel list
5. Send the link to the participant via email. Send the password via a separate, secure channel (i.e. WhatsApp, Signal, iMessage or snail mail).

Recommendation: In your mail, make sure to mention that this MRI was not part of a diagnostic procedure and should not be treated as such. 