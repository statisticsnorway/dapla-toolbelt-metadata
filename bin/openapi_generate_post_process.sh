#!/usr/local/bin/bash

FILE_PATH=$1

if [[ $FILE_PATH =~ generated/test/.*\.py ]]; then
    echo "Fixing absolute imports in test file $FILE_PATH"
    sed -i "" "s/from vardef_client./from ..vardef_client./" "$FILE_PATH"

else
    if [[ $FILE_PATH =~ generated/vardef_client/.*/.*\.py ]]; then
        echo "Fixing absolute imports in submodule file $FILE_PATH"
        DOTS=".."
    else
        echo "Fixing absolute imports in main module file $FILE_PATH"
        # Depending on where the file is located we need different numbers of dots in the relative import
        DOTS="."
    fi

    sed -i "" "s/from vardef_client./from $DOTS/" "$FILE_PATH"
    sed -i "" "s/import vardef_client./from $DOTS import /" "$FILE_PATH"
fi

ruff format "$FILE_PATH"
