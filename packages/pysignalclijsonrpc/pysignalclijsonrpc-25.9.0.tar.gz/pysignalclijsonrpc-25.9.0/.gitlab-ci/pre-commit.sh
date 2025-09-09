#!/bin/sh

set -e

apk --no-cache --quiet --no-progress add \
    mise \
    git \
    libmagic
git fetch origin
mise install
mise x -- uv sync --all-groups
mise x -- pre-commit run -a
