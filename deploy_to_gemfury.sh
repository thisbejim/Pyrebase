#!/bin/bash
#
# Build a Python distributable and push to Gemfury [https://gemfury.com/].
#
# This script should work with any Python codebase which uses setup.py.
# To run, the environment variable $GEMFURY_REPO_URL must be set to the
# appropriate Gemfury repository URL, which is usually kept secret and not
# checked into the codebase.
#
###########################################################################

# Exit on error
set -e

if [ -z "$GEMFURY_REPO_URL" ];
then
    printf 'GEMFURY_REPO_URL must be set.\n' >&2
    exit 1
fi

python setup.py sdist

pushd dist >/dev/null
filename=$(ls -t . | head -n1)
curl -F package=@$filename $GEMFURY_REPO_URL
popd >/dev/null