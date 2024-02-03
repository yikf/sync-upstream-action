#!/bin/bash

pip3 install -r /sync-upstream/requirements.txt

python3 /sync-upstream/sync.py \
--token "${INPUT_TOKEN}" \
--owner "${INPUT_OWNER}" \
--repo "${INPUT_REPO}" \
--branch "${INPUT_BRANCH}"