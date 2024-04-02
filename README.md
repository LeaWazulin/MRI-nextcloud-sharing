# MRI-nextcloud-sharing
Share password-protected MRI images via Nextcloud

## preparation

install the following via pip
`pip install dicom2nifti wordfreq tqdm pyminizip`

## usage

1. edit the password/username etc in the `share_with_password.py`

```
    username = 'usename'             # user name for nextcloud
    password = 'password'     # password for the user
    remote_path = 'MRI-share'        # folder in which the files are uploaded
    nextcloud_baseurl = 'https://cloud.skjerns.de'  # server URL
```

2. run script via `python share_with_password.py` and select the folder that contains the DICOM folders
3. There will be a `share-list.xlsx` inside 
