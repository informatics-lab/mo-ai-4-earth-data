#! /usr/bin/env bash
set -ex

source .env

cd __app__

#  Create resource group if not exists
if [ $(az group exists --resource-group ${RESOURCE_GROUP}) == "false" ]; then
    az group create --name $RESOURCE_GROUP --location $RESOURCE_LOCATION
fi

#  Create storage acccount if not exists
if ! az storage account show --resource-group ${RESOURCE_GROUP} --name $STORAGE_ACCOUNT_NAME >/dev/null 2>&1 ; then
    az storage account create --resource-group ${RESOURCE_GROUP} --name $STORAGE_ACCOUNT_NAME
fi
FUNC_STORAGE_CONN_STR=$(az storage account show-connection-string --name $STORAGE_ACCOUNT_NAME --resource-group ${RESOURCE_GROUP} --query "connectionString" -o tsv)

if ! az functionapp show --name $APP_NAME  --resource-group $RESOURCE_GROUP >/dev/null 2>&1 ; then
    # using westeurope beacuse of this https://stackoverflow.com/questions/53790218/error-scale-operation-is-not-allowed-for-this-subscription-in-this-region-when
    az functionapp create --name $APP_NAME \
    --name $APP_NAME \
    --storage-account $STORAGE_ACCOUNT_NAME\
    --consumption-plan-location westeurope \
    --resource-group $RESOURCE_GROUP \
    --runtime python \
    --runtime-version 3.7 \
    --os-type Linux
fi


#  Create service bus namespace name is avaliable (i.e. it doesn't already exist)
# if [ $(az servicebus namespace exists --name ${SERVICE_BUS_NAMESPACE} --query nameAvailable -o tsv) == "true" ];then
if ! az servicebus namespace list --query "[].name" -o tsv | grep "${SERVICE_BUS_NAMESPACE}" >/dev/null 2>&1 ; then
    az servicebus namespace create \
        --name  $SERVICE_BUS_NAMESPACE \
        --resource-group $RESOURCE_GROUP \
        --location $RESOURCE_LOCATION \
        --sku "Basic"
fi


#  Create service queues if not exists
if ! az servicebus queue show --resource-group $RESOURCE_GROUP --namespace-name $SERVICE_BUS_NAMESPACE --name $DATA_QUEUE_NAME  >/dev/null 2>&1 ; then
        az servicebus queue create \
            --resource-group $RESOURCE_GROUP \
            --namespace-name $SERVICE_BUS_NAMESPACE \
            --name $DATA_QUEUE_NAME  \
            --default-message-time-to-live PT3H \
            --lock-duration PT2M \
            --max-delivery-count 5
fi 


# One for subscription messages
if ! az servicebus queue show --resource-group $RESOURCE_GROUP --namespace-name $SERVICE_BUS_NAMESPACE --name $SUBSCRIBE_QUEUE_NAME  >/dev/null 2>&1 ; then
        az servicebus queue create \
            --resource-group $RESOURCE_GROUP \
            --namespace-name $SERVICE_BUS_NAMESPACE \
            --name $SUBSCRIBE_QUEUE_NAME  \
            --default-message-time-to-live P5D \
            --lock-duration PT1M \
            --max-delivery-count 10 \
            --max-size 1024
fi  

# Set up access for service bus
if ! az servicebus namespace authorization-rule show --resource-group $RESOURCE_GROUP --namespace-name $SERVICE_BUS_NAMESPACE  --name $SERVICE_BUS_ACCESS_KEY_NAME  >/dev/null 2>&1 ; then
    az servicebus namespace authorization-rule create --resource-group $RESOURCE_GROUP --namespace-name $SERVICE_BUS_NAMESPACE  --name $SERVICE_BUS_ACCESS_KEY_NAME --rights Send Listen
fi
SERVICE_BUS_KEYS=$(az servicebus namespace authorization-rule keys list --resource-group $RESOURCE_GROUP --namespace-name $SERVICE_BUS_NAMESPACE --name $SERVICE_BUS_ACCESS_KEY_NAME --query primaryConnectionString -o tsv)

# Get subscription and keys for AI for Earth storage account
AI_FOR_EARTH_SUB_ID=$(az account list --query "[?(@.name=='$AI_FOR_EARTH_SUB_NAME')].id" -o tsv)
AI_FOR_EARTH_CONN_STR=$(az storage account show-connection-string --name $AI_FOR_EARTH_STORAGE_ACCOUNT_NAME --subscription $AI_FOR_EARTH_SUB_ID --query "connectionString" -o tsv)

# Create container if doesn't exist
if ! az storage container show --connection-string $AI_FOR_EARTH_CONN_STR --name $CONTAINER_NAME  >/dev/null 2>&1 ; then
    az storage container create --connection-string $AI_FOR_EARTH_CONN_STR --name $CONTAINER_NAME  
fi

# Set up function vars
func settings add AzureWebJobsStorage $FUNC_STORAGE_CONN_STR
func settings add DATA_QUEUE_NAME $DATA_QUEUE_NAME
func settings add SUBSCRIBE_QUEUE_NAME $SUBSCRIBE_QUEUE_NAME
func settings add CONTAINER_NAME $CONTAINER_NAME
func settings add ServiceBusConnection $SERVICE_BUS_KEYS
func settings add AI_FOR_EARTH_CONN_STR $AI_FOR_EARTH_CONN_STR
# func settings add AI_FOR_EARTH_STORAGE_ACCOUNT_NAME $AI_FOR_EARTH_STORAGE_ACCOUNT_NAME