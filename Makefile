.PHONY: install-openapi-generator
install-openapi-generator:
	brew install openapi-generator

.PHONY: generate-vardef-client
generate-vardef-client:
	openapi-generator generate -i https://metadata.test.ssb.no/docs/openapi/variable-definitions-0.1.yml -g python -o src/dapla_metadata/variable_definitions/generated --skip-validate-spec
