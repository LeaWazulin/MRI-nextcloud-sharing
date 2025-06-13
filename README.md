# MRI-nextcloud-sharing

Share password-protected MRI MPRAGE images via Nextcloud. 
Uploads NIFTI files to Nextcloud zipped with a random password.
You send the link to the NIFTI via mail and the password via a secure second channel e.g. WhatsApp or Signal.

![image](https://github.com/CIMH-Clinical-Psychology/MRI-nextcloud-sharing/assets/14980558/b8e78dc5-2c01-49db-97a7-5de3b46c124f)

## preparation

- clone this repository to your local machine
- install the following via pip:  `pip install wordfreq tqdm pyminizip --trusted-host pypi.org --trusted-host files.pythonhosted.org ` or use `pip install -r requirements.txt`

  then enter your credentials into `credentials.json`

PS: Best practice is to create an API [app password](https://help.nextcloud.com/t/where-to-create-app-password/157454/2) in the Nextcloud settings under "security". 
Don't store your actual user password in plain text on disc, only the app password.

```json
   {"username": "firstname.lastname",         # user name for nextcloud
    "password": "password",         # password for the user
    "remote_path": "MRI-share",     # folder on nextcloud in which the files are uploaded. Needs to exist already.
    "expiration_days": 21,          # delete share after this time
    "include_mricron": true,        # include a program to view NIFTI files (Windows only)
    "nextcloud_baseurl": "https://cloud.zi-mannheim.de"  # server URL of ZI nextcloud
```

## data structure

The script expects BIDS data structure in the form of

```
├───mri_images
│   ├───subj1
│   │       anat
│   │         subj1_T1w.nii.gz
│   │       func     
│   │       ....
│   ├───subj2
│   │       anat
│           func  
│   └───subj3


## usage

1. run script via `python share_with_password.py` and select the folder of your
   BIDs data of all participants (BIDs root folder i.e. the folder above the actual subject folders)
2. The script will create random passwords and upload the files to nextcloud
3. A `share-list.xlsx` will be created containing all the links and passwords.
4. In the end, the script will ask you, in which directory you want to save
   the share-list.xlsx (orginial BIDs root folder/data structure remains unchanged!)
5. If you need to re-share a file, simply delete the row of the participant from the excel list
6. Send the link to the participant via email. Send the password via a separate, secure channel (i.e. WhatsApp, Signal, iMessage or snail mail).

There is a sample mail available here: [mail template](https://github.com/CIMH-Clinical-Psychology/MRI-nextcloud-sharing/blob/main/sample_mail.txt)
