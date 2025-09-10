#!/bin/bash

# envsh-utils.sh - Utility functions for working with associative arrays
# This file is automatically installed with the envsh Python package

# Convert associative array to JSON string
# Usage: _convert_array_to_json <array_name>
_convert_array_to_json() {
    local -n profile=$1
    local json="{"
    for key in "${!profile[@]}"; do
        json+="\"$key\": \"${profile[$key]}\","
    done
    echo "${json%,}}"
}

# Export associative array as JSON variable
# Usage: export_array_as_json <array_name> [json_var_name]
export_array_as_json() {
    local source_array_name="$1"
    local destination_variable_name="${2:-${source_array_name}_JSON}"

    if ! declare -p "$source_array_name" 2>/dev/null | grep -q 'declare -A'; then
        echo "Error: Array '$source_array_name' is not declared!" >&2
        return 1
    fi

    local json_value
    json_value=$(_convert_array_to_json "$source_array_name")
    eval "declare -g $destination_variable_name='$json_value'"
    eval "export $destination_variable_name"
}

export -f export_array_as_json

# Check if this script is being sourced (recommended usage)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Warning: This script should be sourced, not executed directly."
    echo "Usage: source envsh-utils.sh"
fi
