#!/bin/sh

set -e

apk --no-cache --quiet --no-progress add \
    mise \
    git \
    libmagic \
    build-base
mise install
mise docs
