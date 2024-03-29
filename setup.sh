#!/bin/bash

# Create a stack instance according to the parameters supplied in the
# environment variables. For an example configuration, see config.sh

####################################################

source config.sh

source create.sh clean

# Get the Security Group ID corresponding to SEC_GRP_NAME
SEC_GRP_ID=$(aws ec2 describe-security-groups \
--group-names $SEC_GRP_NAME | \
python3 -c \
"import sys, json
print(json.load(sys.stdin)['SecurityGroups'][0]['GroupId'])")

# List the subnets which the RDS is on
SUBNETS=$(aws rds describe-db-instances \
--db-instance-identifier $RDS_INSTANCE_NAME | \
python3 -c \
"import sys, json
sng = json.load(sys.stdin)['DBInstances'][0]['DBSubnetGroup']
subnets = sng['Subnets'][0]['SubnetIdentifier']
for s in sng['Subnets'][1:]:
    subnets += (',' + s['SubnetIdentifier'])
print(subnets)")


source create.sh stack \
"VPCsecurityGroupID=$SEC_GRP_ID VPCsubnetIDlist=$SUBNETS timeout=$LAMBDA_TIMEOUT_SEC"

QUEUE_NAME="${FUNCTION_NAME}-queue"
echo "Created queue: $QUEUE_NAME"

# Add environment variables to the lambda
aws lambda update-function-configuration \
--function-name $FUNCTION_NAME \
--environment "Variables={DB_PORT=$DB_PORT, \
DB_USER=$DB_USER, DB_NAME=$DB_NAME, \
DB_HOST=$DB_HOST, DB_PASSWORD=$DB_PASSWORD, \
LOG_LEVEL=$LOG_LEVEL, DB_DIALECT_DRIVER=$DB_DIALECT_DRIVER}" &> /dev/null
