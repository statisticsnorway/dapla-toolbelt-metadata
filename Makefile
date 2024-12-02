.PHONY: install-openapi-generator
install-openapi-generator:
	brew install openapi-generator

.PHONY: generate-vardef-client
generate-vardef-client:
	export PYTHON_POST_PROCESS_FILE="bin/openapi_generate_post_process.sh" && \
	openapi-generator generate \
		--enable-post-process-file \
		-i https://metadata.test.ssb.no/docs/openapi/variable-definitions-0.1.yml \
		-g python \
		-o src/dapla_metadata/variable_definitions/generated \
		--additional-properties=packageName=vardef_client \
		--skip-validate-spec
