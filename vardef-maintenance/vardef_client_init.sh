#! /bin/bash

# Retrieve the vardef interface notebooks and put them in the /home/onyxia/work/variable_definitions directory
git clone -n --depth=1 --filter=tree:0 \
  https://github.com/statisticsnorway/dapla-toolbelt-metadata.git $HOME/tmp/dapla-toolbelt-metadata
pushd "$HOME"/tmp/dapla-toolbelt-metadata || exit
git sparse-checkout set --no-cone /demo/variable_definitions --no-cone vardef-maintenance/vardef-maintenance.toml
git checkout
cp -R demo/variable_definitions "$HOME"/work/variable_definitions
cp vardef-maintenance/vardef-maintenance.toml "$HOME"/work/variable_definitions/pyproject.toml
popd || exit
rm -rf "$HOME"/tmp/dapla-toolbelt-metadata
pushd "$HOME"/work/variable_definitions || exit
ssb-project build --no-verify
