"""Variable Definitions

## Introduction  Variable Definitions are centralized definitions of concrete variables which are typically present in multiple datasets. Variable Definitions support standardization of data and metadata and facilitate sharing and joining of data by clarifying when variables have an identical definition.  ## Maintenance of Variable Definitions This API allows for creation, maintenance and access of Variable Definitions.  ### Ownership Creation and maintenance of variables may only be performed by Statistics Norway employees representing a specific Dapla team, who are defined as the owners of a given Variable Definition. The team an owner represents must be specified when making a request through the `active_group` query parameter. All maintenance is to be performed by the owners, with no intervention from administrators.  ### Status All Variable Definitions have an associated status. The possible values for status are `DRAFT`, `PUBLISHED_INTERNAL` and `PUBLISHED_EXTERNAL`.   #### Draft When a Variable Definition is created it is assigned the status `DRAFT`. Under this status the Variable Definition is:  - Only visible to Statistics Norway employees. - Mutable (it may be changed directly without need for versioning). - Not suitable to refer to from other systems.  This status may be changed to `PUBLISHED_INTERNAL` or `PUBLISHED_EXTERNAL` with a direct update.  #### Published Internal Under this status the Variable Definition is:  - Only visible to Statistics Norway employees. - Immutable (all changes are versioned). - Suitable to refer to in internal systems for statistics production. - Not suitable to refer to for external use (for example in Statistikkbanken).  This status may be changed to `PUBLISHED_EXTERNAL` by creating a Patch version.  #### Published External Under this status the Variable Definition is:  - Visible to the general public. - Immutable (all changes are versioned). - Suitable to refer to from any system.  This status may not be changed as it would break immutability. If a Variable Definition is no longer relevant then its period of validity should be ended by specifying a `valid_until` date in a Patch version.  ### Immutability Variable Definitions are immutable. This means that any changes must be performed in a strict versioning system. Consumers can avoid being exposed to breaking changes by specifying a `date_of_validity` when they request a Variable Definition.  #### Patches Patches are for changes which do not affect the fundamental meaning of the Variable Definition.  #### Validity Periods Validity Periods are versions with a period defined by a `valid_from` date and optionally a `valid_until` date. If the fundamental meaning of a Variable Definition is to be changed, it should be done by creating a new Validity Period.

The version of the OpenAPI document: 0.1
Contact: metadata@ssb.no
Generated by OpenAPI Generator (https://openapi-generator.tech)

Do not edit the class manually.
"""

import io
import json
import re
import ssl

import urllib3

from .exceptions import ApiException
from .exceptions import ApiValueError

SUPPORTED_SOCKS_PROXIES = {"socks5", "socks5h", "socks4", "socks4a"}
RESTResponseType = urllib3.HTTPResponse


def is_socks_proxy_url(url):
    if url is None:
        return False
    split_section = url.split("://")
    if len(split_section) < 2:
        return False
    return split_section[0].lower() in SUPPORTED_SOCKS_PROXIES


class RESTResponse(io.IOBase):
    def __init__(self, resp) -> None:
        self.response = resp
        self.status = resp.status
        self.reason = resp.reason
        self.data = None

    def read(self):
        if self.data is None:
            self.data = self.response.data
        return self.data

    def getheaders(self):
        """Returns a dictionary of the response headers."""
        return self.response.headers

    def getheader(self, name, default=None):
        """Returns a given response header."""
        return self.response.headers.get(name, default)


class RESTClientObject:
    def __init__(self, configuration) -> None:
        # urllib3.PoolManager will pass all kw parameters to connectionpool
        # https://github.com/shazow/urllib3/blob/f9409436f83aeb79fbaf090181cd81b784f1b8ce/urllib3/poolmanager.py#L75
        # https://github.com/shazow/urllib3/blob/f9409436f83aeb79fbaf090181cd81b784f1b8ce/urllib3/connectionpool.py#L680
        # Custom SSL certificates and client certificates: http://urllib3.readthedocs.io/en/latest/advanced-usage.html

        # cert_reqs
        if configuration.verify_ssl:
            cert_reqs = ssl.CERT_REQUIRED
        else:
            cert_reqs = ssl.CERT_NONE

        pool_args = {
            "cert_reqs": cert_reqs,
            "ca_certs": configuration.ssl_ca_cert,
            "cert_file": configuration.cert_file,
            "key_file": configuration.key_file,
        }
        if configuration.assert_hostname is not None:
            pool_args["assert_hostname"] = configuration.assert_hostname

        if configuration.retries is not None:
            pool_args["retries"] = configuration.retries

        if configuration.tls_server_name:
            pool_args["server_hostname"] = configuration.tls_server_name

        if configuration.socket_options is not None:
            pool_args["socket_options"] = configuration.socket_options

        if configuration.connection_pool_maxsize is not None:
            pool_args["maxsize"] = configuration.connection_pool_maxsize

        # https pool manager
        self.pool_manager: urllib3.PoolManager

        if configuration.proxy:
            if is_socks_proxy_url(configuration.proxy):
                from urllib3.contrib.socks import SOCKSProxyManager

                pool_args["proxy_url"] = configuration.proxy
                pool_args["headers"] = configuration.proxy_headers
                self.pool_manager = SOCKSProxyManager(**pool_args)
            else:
                pool_args["proxy_url"] = configuration.proxy
                pool_args["proxy_headers"] = configuration.proxy_headers
                self.pool_manager = urllib3.ProxyManager(**pool_args)
        else:
            self.pool_manager = urllib3.PoolManager(**pool_args)

    def request(
        self,
        method,
        url,
        headers=None,
        body=None,
        post_params=None,
        _request_timeout=None,
    ):
        """Perform requests.

        :param method: http request method
        :param url: http request url
        :param headers: http request headers
        :param body: request json body, for `application/json`
        :param post_params: request post parameters,
                            `application/x-www-form-urlencoded`
                            and `multipart/form-data`
        :param _request_timeout: timeout setting for this request. If one
                                 number provided, it will be total request
                                 timeout. It can also be a pair (tuple) of
                                 (connection, read) timeouts.
        """
        method = method.upper()
        assert method in [
            "GET",
            "HEAD",
            "DELETE",
            "POST",
            "PUT",
            "PATCH",
            "OPTIONS",
        ]

        if post_params and body:
            raise ApiValueError(
                "body parameter cannot be used with post_params parameter.",
            )

        post_params = post_params or {}
        headers = headers or {}

        timeout = None
        if _request_timeout:
            if isinstance(_request_timeout, (int, float)):
                timeout = urllib3.Timeout(total=_request_timeout)
            elif isinstance(_request_timeout, tuple) and len(_request_timeout) == 2:
                timeout = urllib3.Timeout(
                    connect=_request_timeout[0],
                    read=_request_timeout[1],
                )

        try:
            # For `POST`, `PUT`, `PATCH`, `OPTIONS`, `DELETE`
            if method in ["POST", "PUT", "PATCH", "OPTIONS", "DELETE"]:
                # no content type provided or payload is json
                content_type = headers.get("Content-Type")
                if not content_type or re.search("json", content_type, re.IGNORECASE):
                    request_body = None
                    if body is not None:
                        request_body = json.dumps(body)
                    r = self.pool_manager.request(
                        method,
                        url,
                        body=request_body,
                        timeout=timeout,
                        headers=headers,
                        preload_content=False,
                    )
                elif content_type == "application/x-www-form-urlencoded":
                    r = self.pool_manager.request(
                        method,
                        url,
                        fields=post_params,
                        encode_multipart=False,
                        timeout=timeout,
                        headers=headers,
                        preload_content=False,
                    )
                elif content_type == "multipart/form-data":
                    # must del headers['Content-Type'], or the correct
                    # Content-Type which generated by urllib3 will be
                    # overwritten.
                    del headers["Content-Type"]
                    # Ensures that dict objects are serialized
                    post_params = [
                        (a, json.dumps(b)) if isinstance(b, dict) else (a, b)
                        for a, b in post_params
                    ]
                    r = self.pool_manager.request(
                        method,
                        url,
                        fields=post_params,
                        encode_multipart=True,
                        timeout=timeout,
                        headers=headers,
                        preload_content=False,
                    )
                # Pass a `string` parameter directly in the body to support
                # other content types than JSON when `body` argument is
                # provided in serialized form.
                elif isinstance(body, str) or isinstance(body, bytes):
                    r = self.pool_manager.request(
                        method,
                        url,
                        body=body,
                        timeout=timeout,
                        headers=headers,
                        preload_content=False,
                    )
                elif headers["Content-Type"].startswith("text/") and isinstance(
                    body, bool
                ):
                    request_body = "true" if body else "false"
                    r = self.pool_manager.request(
                        method,
                        url,
                        body=request_body,
                        preload_content=False,
                        timeout=timeout,
                        headers=headers,
                    )
                else:
                    # Cannot generate the request from given parameters
                    msg = """Cannot prepare a request message for provided
                             arguments. Please check that your arguments match
                             declared content type."""
                    raise ApiException(status=0, reason=msg)
            # For `GET`, `HEAD`
            else:
                r = self.pool_manager.request(
                    method,
                    url,
                    fields={},
                    timeout=timeout,
                    headers=headers,
                    preload_content=False,
                )
        except urllib3.exceptions.SSLError as e:
            msg = "\n".join([type(e).__name__, str(e)])
            raise ApiException(status=0, reason=msg)

        return RESTResponse(r)