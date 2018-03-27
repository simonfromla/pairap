#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset


celery -A pairup.taskapp worker -l INFO
