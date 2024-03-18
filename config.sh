# Example parameters for creating an instance of this stack.
# Source this script, then run setup.sh

#########################################################

# Name prefix for the resources to be created:
NAME_PREFIX=test2

LOG_LEVEL="DEBUG"

# Security group in the DB's VPC to use:
SEC_GRP_NAME="lambda-rds-1"
RDS_INSTANCE_NAME=testdbi

# Database connection parameters:
DB_PORT=5432
DB_USER=dbuser
DB_NAME=postgres
DB_HOST=testdbi.cvyycu2kubso.eu-west-2.rds.amazonaws.com
# DB_PASSWORD  -> define this separately
DB_DIALECT_DRIVER='postgresql+psycopg2'