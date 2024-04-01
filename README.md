# AWS Lambda DB

![local tests](https://github.com/e-mit/aws-lambda-db/actions/workflows/tests.yml/badge.svg)
![coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/e-mit/9df92671b4e2859b1e75cf762121b73f/raw/aws-lambda-db.json)
![flake8](https://github.com/e-mit/aws-lambda-db/actions/workflows/flake8.yml/badge.svg)
![mypy](https://github.com/e-mit/aws-lambda-db/actions/workflows/mypy.yml/badge.svg)
![pycodestyle](https://github.com/e-mit/aws-lambda-db/actions/workflows/pycodestyle.yml/badge.svg)
![pydocstyle](https://github.com/e-mit/aws-lambda-db/actions/workflows/pydocstyle.yml/badge.svg)
![pylint](https://github.com/e-mit/aws-lambda-db/actions/workflows/pylint.yml/badge.svg)
![pyright](https://github.com/e-mit/aws-lambda-db/actions/workflows/pyright.yml/badge.svg)
![bandit](https://github.com/e-mit/aws-lambda-db/actions/workflows/bandit.yml/badge.svg)

Creates an AWS Lambda function which receives data from a AWS SQS queue and stores it in an SQL database.

This project uses Pydantic, SQLAlchemy, SQLModel, psycopg2. AWS is configured with the CLI and CloudFormation/SAM template.


### See also

- [github.com/e-mit/aws-lambda-get](https://github.com/e-mit/aws-lambda-get) creates an AWS Lambda which executes a periodic HTTP GET request of a REST API and puts the resulting data into a SQS queue.
- [github.com/e-mit/aws-create-db](https://github.com/e-mit/aws-create-db) creates and configures an AWS Relational Database Service (RDS) instance running PostgreSQL.
- [github.com/e-mit/aws-ec2-grafana](https://github.com/e-mit/aws-ec2-grafana) for configuring and deploying Grafana on an EC2 instance to display a public data dashboard


### Readme Contents

- **[Testing](#testing)**<br>
- **[Deployment](#deployment)**<br>
- **[Development](#development)**<br>


## Testing

Tests and linting checks run via GitHub actions after each push. Tests can be run locally (no interaction with AWS), or with AWS (cloud tests).

### Local tests

1. **Optional**: provide a PostgreSQL database server for testing, else the tests will use SQLite only.
    - The following environment variables must be set before running the tests: TEST_DB_PORT, TEST_DB_USER, TEST_DB_NAME, TEST_DB_HOST, TEST_DB_PASSWORD, TEST_DB_DIALECT_DRIVER
    - The database named ```TEST_DB_NAME``` must already exist.
    - Only ```TEST_DB_DIALECT_DRIVER='postgresql+psycopg2'``` is supported.
2. Run all tests and linting with ```test.sh```

### Cloud tests

TODO


## Deployment

1. Provide values for the environment variables listed in ```config.sh```
2. Execute script ```setup.sh```. This will create the resources and start the lambda. A file "id.txt" is created which stores a random number used for uniqueness.
3. Change log level using: ```./create.sh loglevel <log level string e.g. DEBUG>```
4. Stop the lambda and delete all resources using: ```./create.sh clean```


## Development

After deploying the stack, the lambda code and the packaged Python library dependencies can be updated independently, and rapidly, using the following commands:

- Lambda function update: ```./create.sh update_function```
- Python packages update: ```./create.sh update_layer```
