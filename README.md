# NTAP-projects
Collection of scripts for NTAP cloud products

## CVO-GCP
Collection of scripts for Cloud Volumes ONTAP in GCP

### Contents:
- <a href="https://github.com/felix-melligan/NTAP-projects/blob/main/CVO-GCP/gcp_cvo_deploy_test.py">/CVO-GCP/gcp_cvo_deploy_test.py</a>
  - Tests GCP environment configuration to help troubleshoot/check
  - To use:
   - Deploy the Cloud Manager Service connector (Or a VM with the Cloud Manager service account into GCP)
   - ssh into the service connector VM
   - Copy contents of file into a fresh .py file onto the service connector VM in GCP:
   
   ```
   vi gcp_test.py
   
   i
   
   [Ctrl+V]
   
   [ESC]
   
   :wq
   
   [ENTER]
   ```
   
   - Install pip:
   
   ```
   sudo su
   
   yum install python-pip
   ```
   
   - Install requests package:

   ```
   pip install requests
   ```
   
   - Change variables (if applicable)
   - Run script:
   
   ```
   python gcp_test.py
   ```
   

- <a href="https://github.com/felix-melligan/NTAP-projects/blob/main/CVO-GCP/cvo-gcp-setup.sh">/CVO-GCP/cvo-gcp-setup.sh</a>
  - Prepares GCP environment to deploy Cloud Volumes ONTAP and Service Connector
  - Must be Editor/Owner in host & service project to use
  - Must run script from gcloud CLI in service project
