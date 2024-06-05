# Example parameters for creating an instance of this stack.
# Source this script, then run setup.sh

#########################################################

# Name prefix for the resources to be created
NAME_PREFIX=lambda-db-test5

# Lambda CloudWatch log level
LOG_LEVEL=ERROR

# Lambda timeout:
LAMBDA_TIMEOUT_SEC=10

# The name of the RDS instance to use
RDS_INSTANCE_NAME=testdbi

# Security group in the database's VPC to use
SEC_GRP_NAME=lambda-rds-1

# Database connection parameters
DB_PORT=5432
DB_USER=dbuser
DB_NAME=postgres
DB_HOST=testdbi.cvyycu2kubso.eu-west-2.rds.amazonaws.com
# DB_PASSWORD  -> define this separately
DB_DIALECT_DRIVER=postgresql+psycopg2