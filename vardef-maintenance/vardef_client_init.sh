#! /bin/bash

BRANCH="main"
BASE_DIR=$HOME

while [ "$#" -gt 0 ]; do
  case "$1" in
    --branch=*) BRANCH="${1#*=}"; shift 1;;
    --base-dir=*) BASE_DIR="${1#*=}"; shift 1;;
    --branch|--base-dir) echo "$1 requires an argument" >&2; exit 1;;

    -*) echo "unknown option: $1" >&2; exit 1;;
    *) handle_argument "$1"; shift 1;;
  esac
done

TMP_CHECKOUT_DIR="$BASE_DIR"/tmp/dapla-toolbelt-metadata
VARIABLE_DEFINITIONS_DIR="$BASE_DIR"/work/variable_definitions
mkdir -p "$VARIABLE_DEFINITIONS_DIR"

echo "Retrieve the notebooks from statisticsnorway/dapla-toolbelt-metadata"
# Retrieve the vardef interface notebooks and put them in the /home/onyxia/work/variable_definitions directory
git clone -n --filter=tree:0 \
  https://github.com/statisticsnorway/dapla-toolbelt-metadata.git "$TMP_CHECKOUT_DIR"
pushd "$TMP_CHECKOUT_DIR" || exit
git sparse-checkout set --no-cone /demo/variable_definitions --no-cone /vardef-maintenance/vardef-maintenance.toml
git checkout "$BRANCH"
cp -R demo/variable_definitions "$VARIABLE_DEFINITIONS_DIR"
cp vardef-maintenance/vardef-maintenance.toml "$VARIABLE_DEFINITIONS_DIR"/pyproject.toml
popd || exit
rm -rf "$TMP_CHECKOUT_DIR"

echo "Run ssb-project build"
pushd "$VARIABLE_DEFINITIONS_DIR" || exit
ssb-project build --no-verify
