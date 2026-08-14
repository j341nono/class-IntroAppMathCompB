#!/usr/bin/env bash

set -euo pipefail

readonly ENV_NAME="hpi-assignment"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

find_conda() {
    if command -v conda >/dev/null 2>&1; then
        command -v conda
        return
    fi

    if [[ -n "${CONDA_EXE:-}" && -x "${CONDA_EXE}" ]]; then
        printf '%s\n' "${CONDA_EXE}"
        return
    fi

    local candidate
    for candidate in \
        "${HOME}/miniforge3/bin/conda" \
        "${HOME}/miniconda3/bin/conda" \
        "${HOME}/anaconda3/bin/conda"; do
        if [[ -x "${candidate}" ]]; then
            printf '%s\n' "${candidate}"
            return
        fi
    done

    printf '%s\n' "Error: conda was not found. Install Miniforge or Anaconda first." >&2
    return 1
}

CONDA_COMMAND="$(find_conda)"
cd "${PROJECT_DIR}"

if "${CONDA_COMMAND}" env list | awk '{print $1}' | grep -Fxq "${ENV_NAME}"; then
    echo "Updating Conda environment: ${ENV_NAME}"
    "${CONDA_COMMAND}" env update \
        --name "${ENV_NAME}" \
        --file environment.yml \
        --prune
else
    echo "Creating Conda environment: ${ENV_NAME}"
    "${CONDA_COMMAND}" env create --file environment.yml
fi

echo "Running all HPI experiments"
"${CONDA_COMMAND}" run --no-capture-output \
    --name "${ENV_NAME}" \
    python src/main.py

echo "Done. See figures/ and results/results.csv."
