#!/bin/bash

pip3 install -r /sync-requirements/requirements.txt

python3 /sync-requirements/sync.py \
--token "${INPUT_TOKEN}" \
--owner "${INPUT_OWNER}" \
--repo "${INPUT_REPO}" \
--branch "${INPUT_BRANCH}"