#!/bin/bash
# Version 1.0.0

# Run this script with one of the following input arguments:
entryFuncs=("clean" "stack" "update_function" "update_layer")

# Additionally: "stack" has an optional 2nd argument, which is a
# space-separated list of parameter-overrides to pass to
# cloudformation deploy, which become template parameters.

ID_FILE_NAME="id.txt"

############################################################

EXTRA_PARAM_OVERRIDES=$2

if [[ -z $NAME_PREFIX ]]; then
    echo ERROR: Please set NAME_PREFIX
    return 1
else
    # Convert to lower-case
    NAME_PREFIX_LOWER="$(echo $NAME_PREFIX | tr '[A-Z]' '[a-z]')"
fi

# Prevent terminal output waiting:
export AWS_PAGER=""

_make_names() {
    FUNCTION_NAME="${NAME_PREFIX}Function$RAND_ID"
    STACK_NAME="${NAME_PREFIX}Stack$RAND_ID"
    BUCKET_NAME="${NAME_PREFIX_LOWER}bucket$RAND_ID" # Lower case only
    LAYER_NAME=$FUNCTION_NAME-layer
}

_get_id() {
    if [ -f $ID_FILE_NAME ]; then
        RAND_ID=$(cat $ID_FILE_NAME)
        _make_names
        echo "Found $STACK_NAME"
        return 0
    fi
    return 1
}

_make_id() {
    RAND_ID=$(dd if=/dev/random bs=3 count=1 2>/dev/null \
                | od -An -tx1 | tr -d ' \t\n')
    echo $RAND_ID > $ID_FILE_NAME
    _make_names
    echo "Creating $STACK_NAME with Lambda $FUNCTION_NAME"
}

_delete_files() {
    rm -rf package function/__pycache__ venv
    rm -f function/*.pyc out.yml *.zip
}

clean() {
    echo "Deleting the stack, resources (lambda and role) and temporary files"

    if _get_id ; then
        aws cloudformation delete-stack --stack-name $STACK_NAME
        echo "Deleted $STACK_NAME"

        # Note that the layer(s) are not included in the stack.
        echo "Delete layer (all versions)"
        while true; do
        VERSION=$(aws lambda list-layer-versions \
        --layer-name $LAYER_NAME | \
        python3 -c \
"import sys, json
try:
    print(json.load(sys.stdin)['LayerVersions'][0]['Version'])
except:
    exit(1)")
        if [[ "$?" -ne 0 ]]; then
            break
        fi
        echo Deleting layer $LAYER_NAME:$VERSION
        aws lambda delete-layer-version \
        --layer-name $LAYER_NAME \
        --version-number $VERSION
        done

        echo "Delete the log group (was automatically created but is not in the stack)"
        aws logs delete-log-group --log-group-name /aws/lambda/$FUNCTION_NAME 2> /dev/null
    fi

    _delete_files
    rm -f $ID_FILE_NAME
}

_prepare_packages() {
    _delete_files
    /usr/bin/python3 -m venv venv
    source venv/bin/activate
    pip3 install --target package/python -r requirements.txt &> /dev/null
    pip3 install -r requirements.txt &> /dev/null
    pip3 install -r test_requirements.txt &> /dev/null
}

stack() {
    if _get_id ; then
        echo "Error: a stack id file already exists: please rename or clean"
        return 1
    fi
    _make_id

    echo Making temporary S3 bucket $BUCKET_NAME
    aws s3 mb s3://$BUCKET_NAME

    _prepare_packages

    aws cloudformation package \
    --template-file template.yml \
    --s3-bucket $BUCKET_NAME \
    --output-template-file out.yml &> /dev/null

    aws cloudformation deploy \
    --template-file out.yml \
    --stack-name $STACK_NAME \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides functionName=$FUNCTION_NAME $EXTRA_PARAM_OVERRIDES

    echo Deleting the temporary S3 bucket
    aws s3 rb --force s3://$BUCKET_NAME
}


update_function() {
    if ! _get_id ; then
        echo "No stack id file found."
        return 1
    fi

    _delete_files
    cd function
    zip -r ../function.zip .
    cd ..
    aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://function.zip &> /dev/null
    echo Updated Lambda $FUNCTION_NAME
}


update_layer() {
    if ! _get_id ; then
        echo "No stack id file found."
        return 1
    fi

    _prepare_packages
    cd package
    zip -r ../package.zip . &> /dev/null
    cd ..
    LAYER_ARN=$(aws lambda publish-layer-version \
    --layer-name $LAYER_NAME \
    --description "Python package layer" \
    --zip-file fileb://package.zip \
    --compatible-runtimes python3.10 \
    --compatible-architectures "x86_64" | jq -r '.LayerVersionArn')

    aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --layers $LAYER_ARN &> /dev/null

    echo "Created and assigned layer $LAYER_ARN"
}

################################################

ok=0
for i in "${entryFuncs[@]}"
do
    if [ "$i" == "$1" ]; then
        echo "Executing $i()"
        $i
        ok=1
    fi
done

if (( ok == 0 )); then
    echo "Error: command not recognised"
fi
