#!/usr/bin/env bash

CONFIG_FILEPATH=$(mktemp -t financeager-config-XXXXX)

# Command should succeed with exit code zero
financeager list -C "$CONFIG_FILEPATH" || exit 1

# Command should fail with non-zero exit code
financeager list -C "$CONFIG_FILEPATH" --month 13 && exit 1 || exit 0
