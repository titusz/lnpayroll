#!/usr/bin/env bash
set -euo pipefail


if [ "${AUTO_MIGRATE_AND_INSTALL-false}" == "true" ]; then
    poetry run python -m dev.install
fi

exec "$@"
