#!/bin/bash

NAME_PREFIX=test1

source create.sh clean

source create.sh stack \
"VPCsecurityGroupID=sg-02d35092e3cdbbf42 \
VPCsubnetIDlist=subnet-0e296e482bfaeebb5,subnet-0880df993af0d3b64,subnet-0f52841fea838974e"

source config.sh

aws lambda update-function-configuration \
--function-name $FUNCTION_NAME \
--environment "Variables={DB_PORT=$DB_PORT, \
DB_USER=$DB_USER,DB_NAME=$DB_NAME, \
DB_HOST=$DB_HOST,DB_PASSWORD=$DB_PASSWORD}"

