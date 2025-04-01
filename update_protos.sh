#!/bin/bash

# Run this script from the root directory, to allow import resolution.
# Protos will be output in the same directory they're defined in.

# Action Protos
protoc --proto_path="$PWD" --python_out="$PWD" extensions/roulette/action/proto/action.proto
protoc --proto_path="$PWD" --python_out="$PWD" extensions/roulette/action/proto/roll.proto

# Roulette Configuration
protoc --proto_path="$PWD" --python_out="$PWD" "extensions/roulette/config/roulette_config.proto"

# App Configuration
protoc --proto_path="$PWD" --python_out="$PWD" "settings/app_config.proto"