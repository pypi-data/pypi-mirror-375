#!/bin/bash

set -e

apk --no-cache --quiet --no-progress add \
    mise \
    git \
    libmagic
mise install
mise x -- uv build
mise x -- uv publish
