# -*- coding: utf-8 -*-

import requests
requests.packages.urllib3.disable_warnings()
requests.adapters.DEFAULT_RETRIES = 2

import base64
import json
import subprocess
import shlex
import sys

# Script to test that all pre-requisites are in place to deploy NetApp Cloud Volumes ONTAP


#<<========= CHANGE BELOW VARIABLES IF APPLICABLE =========>>#

# Default variables
HOST_PROJECT = ""        # Change if using shared VPC - leave blank if not
SERVICE_PROJECT = ""     # Project where CVO will be deployed - Deafults to project that this VM is in
proxy = {                       # Change if using proxy
    "proxyIp": "",              # Proxy IP address
    "proxyPort": "",             # Proxy port
    "proxyUser": "",            # (OPTIONAL) Proxy username
    "proxyPassword": base64.b64encode("".encode("utf-8"))         # (OPTIONAL) Proxy password
}
tiering_service_account = ""

#<<========= CHANGE ABOVE VARIABLES IF APPLICABLE =========>>#

access_token = ""

endpoints_enabled = 0

checklist = {
    "tieringAccount": False,
    "tieringUser": False
}

requests_proxy = {}

# Set endpoints (Taken from Wil Shields' script)
gcp_urls = [
    "https://www.googleapis.com",
    "https://api.services.cloud.netapp.com:443",
    "https://cloud.support.netapp.com.s3.us-west-1.amazonaws.com",
    "https://cognito-idp.us-east-1.amazonaws.com",
    "https://cognito-identity.us-east-1.amazonaws.com",
    "https://sts.amazonaws.com",
    "https://cloud-support-netapp-com-accelerated.s3.amazonaws.com",
    "https://cloudmanagerinfraprod.azurecr.io",
    "https://kinesis.us-east-1.amazonaws.com",
    "https://cloudmanager.cloud.netapp.com",
    "https://netapp-cloud-account.auth0.com",
    "https://support.netapp.com:443",
    "https://support.netapp.com/svcgw",
    "https://support.netapp.com/ServiceGW/entitlement",
    "https://eval.lic.netapp.com.s3.us-west-1.amazonaws.com",
    "https://cloud-support-netapp-com.s3.us-west-1.amazonaws.com",
    "https://client.infra.support.netapp.com.s3.us-west-1.amazonaws.com",
    "https://cloud-support-netapp-com-accelerated.s3.us-west-1.amazonaws.com",
    "https://trigger.asup.netapp.com.s3.us-west-1.amazonaws.com",
    "https://ipa-signer.cloudmanager.netapp.com"
]

# Base permissions
gcp_permissions = {
    "permissions": [
      "iam.serviceAccounts.actAs",
      "compute.regionBackendServices.create",
      "compute.regionBackendServices.get",
      "compute.regionBackendServices.list",
      "compute.networks.updatePolicy",
      "compute.backendServices.create",
      "compute.addresses.list",
      "compute.disks.create",
      "compute.disks.createSnapshot",
      "compute.disks.delete",
      "compute.disks.get",
      "compute.disks.list",
      "compute.disks.setLabels",
      "compute.disks.use",
      "compute.firewalls.create",
      "compute.firewalls.delete",
      "compute.firewalls.get",
      "compute.firewalls.list",
      "compute.globalOperations.get",
      "compute.images.get",
      "compute.images.getFromFamily",
      "compute.images.list",
      "compute.images.useReadOnly",
      "compute.instances.attachDisk",
      "compute.instances.create",
      "compute.instances.delete",
      "compute.instances.detachDisk",
      "compute.instances.get",
      "compute.instances.getSerialPortOutput",
      "compute.instances.list",
      "compute.instances.setDeletionProtection",
      "compute.instances.setLabels",
      "compute.instances.setMachineType",
      "compute.instances.setMetadata",
      "compute.instances.setTags",
      "compute.instances.start",
      "compute.instances.stop",
      "compute.instances.updateDisplayDevice",
      "compute.machineTypes.get",
      "compute.networks.get",
      "compute.networks.list",
      "compute.projects.get",
      "compute.regions.get",
      "compute.regions.list",
      "compute.snapshots.create",
      "compute.snapshots.delete",
      "compute.snapshots.get",
      "compute.snapshots.list",
      "compute.snapshots.setLabels",
      "compute.subnetworks.get",
      "compute.subnetworks.list",
      "compute.zoneOperations.get",
      "compute.zones.get",
      "compute.zones.list",
      "compute.instances.setServiceAccount",
      "deploymentmanager.compositeTypes.get",
      "deploymentmanager.compositeTypes.list",
      "deploymentmanager.deployments.create",
      "deploymentmanager.deployments.delete",
      "deploymentmanager.deployments.get",
      "deploymentmanager.deployments.list",
      "deploymentmanager.manifests.get",
      "deploymentmanager.manifests.list",
      "deploymentmanager.operations.get",
      "deploymentmanager.operations.list",
      "deploymentmanager.resources.get",
      "deploymentmanager.resources.list",
      "deploymentmanager.typeProviders.get",
      "deploymentmanager.typeProviders.list",
      "deploymentmanager.types.get",
      "deploymentmanager.types.list",
      "logging.logEntries.list",
      "logging.privateLogEntries.list",
      "resourcemanager.projects.get",
      "storage.buckets.create",
      "storage.buckets.delete",
      "storage.buckets.get",
      "storage.buckets.list",
      "cloudkms.cryptoKeyVersions.useToEncrypt",
      "cloudkms.cryptoKeys.get",
      "cloudkms.cryptoKeys.list",
      "cloudkms.keyRings.list",
      "storage.buckets.update",
      "iam.serviceAccounts.getIamPolicy",
      "iam.serviceAccounts.list",
      "storage.objects.get",
      "storage.objects.list"
    ]
  }

# Tiering permissions
tiering_permissions = {
    "permissions": [
        "resourcemanager.projects.get",
        "storage.buckets.create",
        "storage.buckets.delete",
        "storage.buckets.get",
        "storage.buckets.getIamPolicy",
        "storage.buckets.list",
        "storage.buckets.setIamPolicy",
        "storage.buckets.update",
        "storage.multipartUploads.abort",
        "storage.multipartUploads.create",
        "storage.multipartUploads.list",
        "storage.multipartUploads.listParts",
        "storage.objects.create",
        "storage.objects.delete",
        "storage.objects.get",
        "storage.objects.getIamPolicy",
        "storage.objects.list",
        "storage.objects.setIamPolicy",
        "storage.objects.update"
    ]
}

# Host project permissions
host_project_permissions = {
    "permissions": [
    # deploymentmanager.editor
        "deploymentmanager.deployments.cancelPreview",
        "deploymentmanager.deployments.create",
        "deploymentmanager.deployments.delete",
        "deploymentmanager.deployments.get",
        "deploymentmanager.deployments.list",
        "deploymentmanager.deployments.stop",
        "deploymentmanager.deployments.update",
        "deploymentmanager.manifests.get",
        "deploymentmanager.manifests.list",
        "deploymentmanager.operations.get",
        "deploymentmanager.operations.list",
        "deploymentmanager.resources.get",
        "deploymentmanager.resources.list",
        "resourcemanager.projects.get",
        "serviceusage.quotas.get",
        "serviceusage.services.get",
        "serviceusage.services.list",
        # Compute.networkUser
        "compute.addresses.createInternal",
        "compute.addresses.deleteInternal",
        "compute.addresses.get",
        "compute.addresses.list",
        "compute.addresses.useInternal",
        "compute.externalVpnGateways.get",
        "compute.externalVpnGateways.list",
        "compute.externalVpnGateways.use",
        "compute.firewalls.get",
        "compute.firewalls.list",
        "compute.interconnectAttachments.get",
        "compute.interconnectAttachments.list",
        "compute.interconnects.get",
        "compute.interconnects.list",
        "compute.interconnects.use",
        "compute.networks.access",
        "compute.networks.get",
        "compute.networks.getEffectiveFirewalls",
        "compute.networks.list",
        "compute.networks.listPeeringRoutes",
        "compute.networks.use",
        "compute.networks.useExternalIp",
        "compute.projects.get",
        "compute.regions.get",
        "compute.regions.list",
        "compute.routers.get",
        "compute.routers.list",
        "compute.routes.get",
        "compute.routes.list",
        "compute.serviceAttachments.get",
        "compute.serviceAttachments.list",
        "compute.subnetworks.get",
        "compute.subnetworks.list",
        "compute.subnetworks.use",
        "compute.subnetworks.useExternalIp",
        "compute.targetVpnGateways.get",
        "compute.targetVpnGateways.list",
        "compute.vpnGateways.get",
        "compute.vpnGateways.list",
        "compute.vpnGateways.use",
        "compute.vpnTunnels.get",
        "compute.vpnTunnels.list",
        "compute.zones.get",
        "compute.zones.list",
        "networkservices.endpointConfigSelectors.get",
        "networkservices.endpointConfigSelectors.list",
        "networkservices.endpointConfigSelectors.use",
        "networkservices.httpFilters.get",
        "networkservices.httpFilters.list",
        "networkservices.httpFilters.use",
        "networkservices.httpfilters.get",
        "networkservices.httpfilters.list",
        "networkservices.httpfilters.use",
        "networkservices.operations.get",
        "networkservices.operations.list",
        "resourcemanager.projects.get",
        "servicenetworking.services.get",
        "serviceusage.quotas.get",
        "serviceusage.services.get",
        "serviceusage.services.list"
    ]
}

actual_permissions = {"permissions": []}
missing_permissions_list = []

# Declare some color variables (Taken from Wil Shields' script)
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
NC = "\033[0m" #no color
BOLD = "\033[1m"

# Seperator for viewing purposes
def seperator():
    print("\n")
    print("{BOLD}<===################===>{NC}".format(BOLD=BOLD, NC=NC))

# Welcome and variables check
def welcome():
    print("Hello!")
    print("This script will check your Google environment to make sure it is ready to deploy NetApp Cloud Volumes ONTAP, would you like to keep the default variables? (Yes if already changed variables)")

    reply = str(raw_input(' (y/n): ')).lower().strip()
    if reply[0] == 'y':
        return
    if reply[0] == 'n':
        exit("Please set variables")
    else:
        print("{BOLD}\n\nPlease enter 'y' or 'n'\n\n{NC}".format(BOLD=BOLD, NC=NC))
        return welcome()

# Create access token using local service account
def create_access_token():

    seperator()

    print("{BOLD}Creating Access Token{NC}".format(BOLD=BOLD,NC=NC))
    try:
        access_token = subprocess.check_output('gcloud auth application-default print-access-token', shell=True).strip()
    except:
        print("{RED}Could not perform command: {BOLD}gcloud auth application-default print-access-token{NC}{RED}. Are you sure this instance resides in GCP?{NC}".format(RED=RED, NC=NC, BOLD=BOLD))
        exit(0)

    return access_token

# Set project if none given
def set_project():
    global SERVICE_PROJECT

    seperator()

    print("{BOLD}Setting Project{NC}".format(BOLD=BOLD,NC=NC))
    if SERVICE_PROJECT == "":
        try:
            SERVICE_PROJECT = subprocess.check_output('gcloud config list project --format "value(core.project)"', shell=True).strip()
        except:
            print("{RED}{BOLD}No project found, are you sure this instance resides in GCP?{NC}".format(RED=RED, NC=NC, BOLD=BOLD))
            print("{BOLD}Command failed: gcloud config list project --format 'value(core.project)'{NC}".format(BOLD=BOLD, NC=NC))
            exit(0)

    print("{YELLOW}Project set to: {BOLD}{SERVICE_PROJECT}{NC}".format(YELLOW=YELLOW, BOLD=BOLD, NC=NC, SERVICE_PROJECT=SERVICE_PROJECT))

# Set the service account on this VM
def get_service_account():

    try:
        service_account = subprocess.check_output('gcloud config list account --format "value(core.account)"', shell=True).strip()
    except:
        print("{RED}{BOLD}No service account found, are you sure this instance resides in GCP?{NC}".format(RED=RED, NC=NC, BOLD=BOLD))
        print("{BOLD}Command failed: gcloud config list account --format 'value(core.account)'{NC}".format(BOLD=BOLD, NC=NC))
        exit(0)

    return service_account

# Network check (Taken from Wil Shields' script)
def check_endpoints(endpoint_list):
    global endpoints_enabled
    global proxy
    global requests_proxy

    proxy_enabled = (proxy["proxyIp"] != "")
    response = {}

    if proxy_enabled:
        requests_proxy = {
            "https": "http://{user}:{password}@{proxyIp}:{proxyPort}".format(user=proxy["proxyUser"], password=base64.b64decode(proxy["proxyPassword"]).decode("utf-8"), proxyIp=proxy["proxyIp"], proxyPort=proxy["proxyPort"])
        }

    seperator()

    print("{BOLD}Checking Endpoints{NC}".format(BOLD=BOLD,NC=NC))
    print("Settings state proxy usage is: {BOLD}{proxy_enabled}{NC}".format(proxy_enabled=proxy_enabled, BOLD=BOLD, NC=NC))
    if proxy_enabled:
        print("Proxy settings are: {BOLD}{proxy} {YELLOW}Password encoded{NC}".format(proxy=proxy, BOLD=BOLD, NC=NC, YELLOW=YELLOW))

    for url in endpoint_list:
        try:
            response = requests.get(url=url, verify=False, timeout=1, proxies=requests_proxy)
            print("[ {GREEN}Endpoint reachable: {url}  {NC}]".format(GREEN=GREEN,url=url,NC=NC))
            endpoints_enabled += 1
        except requests.exceptions.ConnectionError:
            print("[ {RED}Endpoint unreachable: {url}  {NC}]".format(RED=RED,url=url,NC=NC))
        except:
            print("{RED}Something went wrong!{NC}".format(RED=RED, NC=NC))

# Permissions check for service account on given project with given permissions
def check_service_account_permissions(project, access_token, permission_set, service_account):

    seperator()

    print("{BOLD}Checking Permissions{NC}".format(BOLD=BOLD,NC=NC))
    service_account = subprocess.check_output('gcloud config list account --format "value(core.account)"', shell=True).strip()

    print("Checking permissions for service account: {BOLD}{service_account}{NC} in project: {BOLD}{project}{NC}.".format(BOLD=BOLD, NC=NC, service_account=service_account, project=project))

    headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {token}".format(token=access_token)
    }

    url = "https://cloudresourcemanager.googleapis.com/v1/projects/{project}:testIamPermissions".format(project=project)

    try:
        actual_permissions = requests.post(url=url, headers=headers, json=permission_set, timeout=2, proxies=requests_proxy).json()
    except:
        print("{RED}Something went wrong with the call to: {url}{NC}".format(RED=RED, url=url, NC=NC))

    return actual_permissions

# Check permissions arrays
def permissions_array_check(permissions_needed, actual_permissions, service_account):

    seperator()

    print("{BOLD}Comparing Permissions{NC}".format(BOLD=BOLD,NC=NC))

    try:
        gcp_permissions_list = permissions_needed["permissions"]
        actual_permissions_list = actual_permissions["permissions"]

        missing_permissions_list = list(set(gcp_permissions_list) - set(actual_permissions_list))

        if len(missing_permissions_list) > 0:
            print("{RED}You are missing: {missing_permissions_list} from this service account: {service_account}!{NC}".format(service_account=service_account, GREEN=GREEN, missing_permissions_list=missing_permissions_list, NC=NC, RED=RED))
        else:
            print("{GREEN}You are not missing any permissions on service account: {service_account}!{NC}".format(service_account=service_account, GREEN=GREEN, NC=NC))
    except:
        print("{RED}Something went wrong with the permissions provided: \n{actual_permissions}{NC}".format(RED=RED, NC=NC, actual_permissions=actual_permissions))
    return missing_permissions_list

# Check if tiering service account exists & Private Google Access
def check_tiering(project, access_token, tiering_service_account, service_account):
    global checklist
    tiering_account_iam_policy = {}

    seperator()

    print("{BOLD}Checking Tiering Capability{NC}".format(BOLD=BOLD,NC=NC))
    print("Checking Service Account: {BOLD}{tiering_service_account}{NC} exists and Service Account: {BOLD}{service_account}{NC} is a member.".format(BOLD=BOLD,NC=NC, service_account=service_account, tiering_service_account=tiering_service_account))


    headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {token}".format(token=access_token)
    }

    get_account_url = "https://iam.googleapis.com/v1/projects/{project}/serviceAccounts/{tiering_service_account}".format(project=project, tiering_service_account=tiering_service_account)
    get_iam_policy_url = "https://iam.googleapis.com/v1/projects/{project}/serviceAccounts/{tiering_service_account}:getIamPolicy".format(project=project, tiering_service_account=tiering_service_account)

    try:
        tiering_account = requests.get(url=get_account_url, headers=headers, timeout=2, proxies=requests_proxy).json()

        if tiering_account["email"] == tiering_service_account:
            print("{GREEN}Service Account: {tiering_service_account} exists!{NC}".format(GREEN=GREEN, tiering_service_account=tiering_service_account, NC=NC))
            checklist["tieringAccount"] = True
        else:
            print("{RED}Service Account: {tiering_service_account} does NOT exist!{NC}".format(RED=RED, tiering_service_account=tiering_service_account, NC=NC))
    except:
        print("{RED}Something went wrong with the call to: {get_account_url}{NC}".format(RED=RED, get_account_url=get_account_url, NC=NC))

    try:
        tiering_account_iam_policy = requests.post(url=get_iam_policy_url, headers=headers, timeout=2, proxies=requests_proxy).json()
    except:
        print("{RED}Something went wrong with the call to: {get_iam_policy_url}{NC}".format(RED=RED, get_iam_policy_url=get_iam_policy_url, NC=NC))

    try:
        for binding in tiering_account_iam_policy["bindings"]:
            if ("serviceAccount:{service_account}".format(service_account=service_account) in binding["members"]) and (binding["role"] == "roles/iam.serviceAccountUser"):
                checklist["tieringUser"] = True
                print("{GREEN}Service Account: {service_account} IS a member of {tiering_service_account} and IS a roles/iam.serviceAccountUser!{NC}".format(GREEN=GREEN, tiering_service_account=tiering_service_account, NC=NC, service_account=service_account))
    except:
        pass

    if checklist["tieringUser"] == False:
        print("{RED}Service Account: {service_account} is {BOLD}NOT{NC}{RED} a member of {tiering_service_account} {BOLD}OR{NC}{RED} does {BOLD}NOT{NC}{RED} have the role: roles/iam.serviceAccountUser!{NC}".format(RED=RED, tiering_service_account=tiering_service_account, BOLD=BOLD, NC=NC, service_account=service_account))

    # =====> Tracking through bug: https://issuetracker.google.com/issues/190794163 <=====
    # print("Checking permissions for service account: {BOLD}{service_account}{NC} in project: {BOLD}{project}{NC}.".format(BOLD=BOLD, NC=NC, service_account=service_account, project=project))
    #
    # token = subprocess.check_output('gcloud auth application-default print-access-token', shell=True).strip()
    #
    # headers = {
    #     "Content-Type": "application/json",
    #     "Authorization": "Bearer {token}".format(token=token)
    # }
    #
    # url = "https://cloudresourcemanager.googleapis.com/v1/projects/{project}:testIamPermissions".format(project=project)
    #
    # try:
    #     actual_permissions = requests.post(url=url, headers=headers, json=tiering_permissions).json()
    # except:
    #     print("{RED}Something went wrong with the call to: {url}{NC}".format(RED=RED, url=url, NC=NC))

def final_checklist(service_project_permissions, service_project_missing_permissions_list, host_project_permissions, host_missing_permissions_list, tiering_service_account, service_account):

    seperator()

    print("{BOLD}In summary:{NC}".format(BOLD=BOLD, NC=NC))

    # Endpoints
    total_endpoints_count = len(gcp_urls)
    if endpoints_enabled == 0:
        print("\t{RED}[x]\tEndpoints: {endpoints_enabled}/{total_endpoints_count}{NC}".format(RED=RED, endpoints_enabled=endpoints_enabled, total_endpoints_count=total_endpoints_count, NC=NC))
    elif endpoints_enabled == len(gcp_urls):
        print("\t{GREEN}[✓]\tEndpoints: {endpoints_enabled}/{total_endpoints_count}{NC}".format(GREEN=GREEN, endpoints_enabled=endpoints_enabled, total_endpoints_count=total_endpoints_count, NC=NC))
    else:
        print("\t{YELLOW}[~]\tEndpoints: {endpoints_enabled}/{total_endpoints_count}{NC}".format(YELLOW=YELLOW, endpoints_enabled=endpoints_enabled, total_endpoints_count=total_endpoints_count, NC=NC))

    # Connector Service Account Permissions - Service
    total_permissions_count = len(service_project_permissions['permissions'])
    missing_permissions_count = len(service_project_missing_permissions_list)
    total_actual_permissions_count = total_permissions_count - missing_permissions_count
    if missing_permissions_count == total_permissions_count:
        print("\t{RED}[x]\tConnector Service Account Permissions: {total_actual_permissions_count}/{total_permissions_count}{NC}".format(RED=RED, total_actual_permissions_count=total_actual_permissions_count, total_permissions_count=total_permissions_count, NC=NC))
    elif missing_permissions_count == 0:
        print("\t{GREEN}[✓]\tConnector Service Account Permissions: {total_permissions_count}/{total_permissions_count}{NC}".format(GREEN=GREEN, total_permissions_count=total_permissions_count, NC=NC))
    else:
        print("\t{YELLOW}[~]\tConnector Service Account Permissions: {total_permissions_count}/{total_permissions_count}{NC}".format(YELLOW=YELLOW, total_permissions_count=total_permissions_count, NC=NC))

    # Tiering Service Account Permissions
    if tiering_service_account == "":
        print("\t{GREEN}{BOLD}No Tiering Service Account selected!{NC}".format(GREEN=GREEN, NC=NC, BOLD=BOLD))
    else:
        if checklist["tieringAccount"] == False:
            print("\t{RED}[x]\tTiering Account {tiering_service_account} does NOT exist{NC}".format(tiering_service_account=tiering_service_account, RED=RED, NC=NC))
        if checklist["tieringAccount"]:
            print("\t{GREEN}[✓]\tTiering Account {tiering_service_account} exists{NC}".format(tiering_service_account=tiering_service_account, GREEN=GREEN, NC=NC))

    # Service Account is a User of Tiering
        if checklist["tieringUser"] == False:
            print("\t{RED}[x]\tConnector Service Account {service_account} is NOT a user of Tiering Service Account {tiering_service_account}{NC}".format(service_account=service_account, tiering_service_account=tiering_service_account, RED=RED, NC=NC))
        if checklist["tieringUser"]:
            print("\t{GREEN}[✓]\tConnector Service Account {service_account} is a user of Tiering Service Account {tiering_service_account}{NC}".format(service_account=service_account, tiering_service_account=tiering_service_account, GREEN=GREEN, NC=NC))

    # Connector Service Account Permissions - Host
    if HOST_PROJECT == "":
        print("\t{GREEN}{BOLD}No Shared VPC selected!{NC}".format(GREEN=GREEN, NC=NC, BOLD=BOLD))
    else:
        host_total_permissions_count = len(host_project_permissions['permissions'])
        host_missing_permissions_count = len(host_missing_permissions_list)
        host_total_actual_permissions_count = host_total_permissions_count - host_missing_permissions_count
        if host_missing_permissions_count == host_total_permissions_count:
            print("\t{RED}[x]\tConnector Service Account Permissions on Host: {host_total_actual_permissions_count}/{host_total_permissions_count}{NC}".format(RED=RED, host_total_actual_permissions_count=host_total_actual_permissions_count, host_total_permissions_count=host_total_permissions_count, NC=NC))
        elif missing_permissions_count == 0:
            print("\t{GREEN}[✓]\tConnector Service Account Permissions on Host: {host_total_permissions_count}/{host_total_permissions_count}{NC}".format(GREEN=GREEN, host_total_permissions_count=host_total_permissions_count, NC=NC))
        else:
            print("\t{YELLOW}[~]\tConnector Service Account Permissions on Host: {host_total_permissions_count}/{host_total_permissions_count}{NC}".format(YELLOW=YELLOW, host_total_permissions_count=host_total_permissions_count, NC=NC))


# All the functions we want to chain
def main():
    welcome()
    set_project()
    access_token = create_access_token()
    service_account = get_service_account()
    check_endpoints(endpoint_list=gcp_urls)
    cm_actual_permissions = check_service_account_permissions(access_token=access_token, project=SERVICE_PROJECT, permission_set=gcp_permissions, service_account=service_account)
    cm_missing_permissions = permissions_array_check(permissions_needed=gcp_permissions, actual_permissions=cm_actual_permissions, service_account=service_account)
    if tiering_service_account != "":
        check_tiering(project=SERVICE_PROJECT, access_token=access_token, tiering_service_account=tiering_service_account, service_account=service_account)
    if HOST_PROJECT != "":
        host_actual_permissions = check_service_account_permissions(access_token=access_token, project=HOST_PROJECT, permission_set=host_project_permissions, service_account=service_account)
        host_missing_permissions = permissions_array_check(permissions_needed=host_project_permissions, actual_permissions=host_actual_permissions, service_account=service_account)
    else:
        host_missing_permissions = {}
    final_checklist(host_project_permissions=host_project_permissions, host_missing_permissions_list=host_missing_permissions, service_project_permissions=gcp_permissions, service_project_missing_permissions_list=cm_missing_permissions, tiering_service_account=tiering_service_account, service_account=service_account)
    exit(0)

main()
