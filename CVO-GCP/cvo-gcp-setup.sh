# Set Variables
PROJECT="default"
NETWORK="default"
SUBNET="default"
REGION="us-east4"
ZONE="us-east4-a"
USER_EMAIL="default"
USER_ROLE_NAME="netappuserrole"
SERVICE_CONNECTOR_ROLE_NAME="netappscrole"
SERVICE_CONNECTOR_SERVICE_ACCOUNT_NAME="netapp-service-connector"
CVO_SERVICE_ACCOUNT_NAME="netapp-cloud-volumes-ontap"
USER_POLICY_LINK="https://occm-sample-policies.s3.amazonaws.com/Setup_As_Service_3.7.3_GCP.yaml"
SC_POLICY_LINK="https://occm-sample-policies.s3.amazonaws.com/Policy_for_Cloud_Manager_3.8.0_GCP.yaml"

function welcome {
    echo "Hello, $USER!"
    echo "This script will prepare your Google project to deploy Cloud Volumes ONTAP and the Service Connector, would you like to keep the default settings?"
}

function main {
    welcome
}

main