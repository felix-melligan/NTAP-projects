# NTAP-projects
Collection of scripts for NTAP cloud products

## CVO-GCP
Collection of scripts for Cloud Volumes ONTAP in GCP

### Contents:
- gcp_cvodeploy_test.py
  - Tests GCP environment configuration to help troubleshoot/check
  - To use:
   - Deploy the Cloud Manager Service connector (Or a VM with the Cloud Manager service account into GCP)
   - Copy contents of file into a fresh .py file onto the service connector VM in GCP:
   
   ```vi gcp_test.py```
   
   ```i```
   
   ```[Ctrl+V]```
   
   ```[ESC]```
   
   ```:wq```
   
   ```[ENTER]```
   
   - Install pip:
   
   ```sudo su```
   
   ``` yum install python-pip```
   
   - Install requests package:

   ```pip install requests```
   
   - Change variables (if applicable)
   - Run script:
   
   ```python gcp_test.py```
   

- cvo-gcp-setup.sh
  - Prepares GCP environment to deploy Cloud Volumes ONTAP and Service Connector
  - Must be Editor/Owner in host & service project to use
  - Must run script from gcloud CLI in service project
