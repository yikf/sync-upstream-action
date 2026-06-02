#!/bin/bash

if [ -n "${INPUT_CONFIG}" ]; then
  /root/.cargo/bin/uv run python /sync_upstream/main.py --config "${INPUT_CONFIG}"
elif [ -n "${INPUT_REPO}" ]; then
  /root/.cargo/bin/uv run python /sync_upstream/main.py \
    --token "${INPUT_TOKEN}" \
    --owner "${INPUT_OWNER}" \
    --repo "${INPUT_REPO}" \
    --branch "${INPUT_BRANCH}"
else
  /root/.cargo/bin/uv run python /sync_upstream/main.py --token "${INPUT_TOKEN}" --owner "${INPUT_OWNER}"
fi
