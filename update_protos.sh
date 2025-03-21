#!/bin/bash

# Run this script from the root directory, to allow import resolution.
# Protos will be output in the same directory they're defined in.
protoc --proto_path="$PWD" --python_out="$PWD" "settings/app_config.proto"
protoc --proto_path="$PWD" --python_out="$PWD" "extensions/roulette/config/roulette_config.proto"