#! /bin/bash

# Install dapla-toolbelt-metadata in base conda environment
pip install dapla-toolbelt-metadata

# Retrieve the vardef interface notebooks and put them in the /home/onyxia/work/variable_definitions directory
git clone -n --depth=1 --filter=tree:0 \
  https://github.com/statisticsnorway/dapla-toolbelt-metadata.git $HOME/tmp/dapla-toolbelt-metadata
pushd $HOME/tmp/dapla-toolbelt-metadata
git sparse-checkout set --no-cone /demo/variable_definitions
git checkout
cp -R demo/variable_definitions $HOME/work/variable_definitions
popd
rm -rf $HOME/tmp/dapla-toolbelt-metadata
