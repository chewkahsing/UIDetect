import ssl
import socket

from urllib.parse import urlparse

from logger import (
    log_info,
    log_warning,
    log_error
)


SSL_TIMEOUT = 5


def check_ssl(url):
    """
    Check whether the website has a valid SSL certificate
    and determine the negotiated TLS protocol version.

    Connection handling:
    - Resolve all available socket addresses.
    - Try each address individually.
    - Apply SSL_TIMEOUT to each TCP connection attempt.
    - Continue to another address when one fails.
    - Perform TLS validation after a TCP connection succeeds.
    """

    log_info(
        f"Checking SSL/TLS: {url}"
    )

    try:

        # --------------------------------------------------
        # Extract Hostname
        # --------------------------------------------------

        hostname = urlparse(url).hostname

        if not hostname:

            log_warning(
                "Invalid hostname."
            )

            return {
                "success": False,
                "status": "Unavailable",
                "sslValid": None,
                "protocol": "Unknown",
                "certificate": False,
                "error": {
                    "code": "INVALID_HOSTNAME",
                    "message":
                        "Unable to extract a valid hostname from the URL."
                }
            }

        log_info(
            f"SSL hostname resolved from URL: {hostname}"
        )

        # --------------------------------------------------
        # Create SSL Context
        # --------------------------------------------------

        context = ssl.create_default_context()

        log_info(
            "SSL context created."
        )

        # --------------------------------------------------
        # Resolve Socket Addresses
        # --------------------------------------------------

        log_info(
            f"Resolving TCP addresses for {hostname}:443"
        )

        addresses = socket.getaddrinfo(
            hostname,
            443,
            type=socket.SOCK_STREAM
        )

        if not addresses:

            log_warning(
                f"No TCP addresses found for {hostname}:443"
            )

            return {
                "success": False,
                "status": "Unavailable",
                "sslValid": None,
                "protocol": "Unknown",
                "certificate": False,
                "error": {
                    "code": "SSL_NO_ADDRESSES",
                    "message":
                        "No network addresses were available for the website."
                }
            }

        log_info(
            f"Resolved {len(addresses)} TCP address candidate(s)."
        )

        # --------------------------------------------------
        # Track Connection Errors
        # --------------------------------------------------

        connection_errors = []

        # --------------------------------------------------
        # Try Each TCP Address
        # --------------------------------------------------

        for address_index, address_info in enumerate(
            addresses,
            start=1
        ):

            family = address_info[0]
            socktype = address_info[1]
            protocol_number = address_info[2]
            sockaddr = address_info[4]

            address_host = sockaddr[0]

            log_info(
                f"TCP connection attempt "
                f"{address_index}/{len(addresses)}: "
                f"{address_host}:443 "
                f"(timeout={SSL_TIMEOUT}s)"
            )

            sock = None

            try:

                # ------------------------------------------
                # Create Socket
                # ------------------------------------------

                sock = socket.socket(
                    family,
                    socktype,
                    protocol_number
                )

                # Explicitly enforce the connection timeout.
                sock.settimeout(
                    SSL_TIMEOUT
                )

                # ------------------------------------------
                # Establish TCP Connection
                # ------------------------------------------

                sock.connect(
                    sockaddr
                )

                log_info(
                    f"TCP connection established to "
                    f"{address_host}:443"
                )

                # ------------------------------------------
                # Explicitly Enforce TLS Timeout
                # ------------------------------------------

                sock.settimeout(
                    SSL_TIMEOUT
                )

                # ------------------------------------------
                # SSL/TLS Handshake
                # ------------------------------------------

                log_info(
                    "Starting SSL/TLS handshake..."
                )

                with context.wrap_socket(
                    sock,
                    server_hostname=hostname
                ) as ssock:

                    # Socket ownership is now handled by
                    # the SSL socket context manager.
                    sock = None

                    log_info(
                        "SSL/TLS handshake completed."
                    )

                    # --------------------------------------
                    # Get TLS Protocol
                    # --------------------------------------

                    protocol = ssock.version()

                    log_info(
                        f"Negotiated TLS protocol: {protocol}"
                    )

                    # --------------------------------------
                    # Get Certificate
                    # --------------------------------------

                    certificate = ssock.getpeercert()

                    log_info(
                        "SSL certificate retrieved."
                    )

                    log_info(
                        f"SSL check completed "
                        f"(TLS={protocol})"
                    )

                    return {
                        "success": True,

                        "status": "Valid",

                        "sslValid": True,

                        "protocol": protocol,

                        "certificate":
                            certificate is not None,

                        "error": None
                    }

            except socket.timeout as error:

                connection_errors.append(
                    f"{address_host}: timeout"
                )

                log_warning(
                    f"TCP connection timed out for "
                    f"{address_host}:443 "
                    f"after {SSL_TIMEOUT} seconds."
                )

            except ConnectionRefusedError as error:

                connection_errors.append(
                    f"{address_host}: connection refused"
                )

                log_warning(
                    f"TCP connection refused by "
                    f"{address_host}:443"
                )

            except OSError as error:

                connection_errors.append(
                    f"{address_host}: {error}"
                )

                log_warning(
                    f"TCP connection failed for "
                    f"{address_host}:443: {error}"
                )

            except ssl.SSLError as error:

                # ------------------------------------------
                # SSL/TLS validation failed after TCP
                # connection was successfully established.
                # ------------------------------------------

                log_error(
                    f"SSL Error for {address_host}: "
                    f"{error}"
                )

                return {
                    "success": False,

                    "status": "Invalid",

                    "sslValid": False,

                    "protocol": "Unknown",

                    "certificate": False,

                    "error": {
                        "code": "SSL_CERTIFICATE_ERROR",
                        "message":
                            "The SSL/TLS connection could not be validated."
                    }
                }

            finally:

                if sock is not None:

                    try:

                        sock.close()

                    except Exception:

                        pass

        # --------------------------------------------------
        # All TCP Address Attempts Failed
        # --------------------------------------------------

        log_error(
            f"Unable to establish a TCP connection to "
            f"{hostname}:443."
        )

        log_error(
            f"Connection attempts: "
            f"{'; '.join(connection_errors)}"
        )

        return {
            "success": False,

            "status": "Unavailable",

            "sslValid": None,

            "protocol": "Unknown",

            "certificate": False,

            "error": {
                "code": "SSL_CONNECTION_FAILED",
                "message":
                    "Unable to establish an SSL/TLS connection "
                    "to the website."
            }
        }

    # --------------------------------------------------
    # DNS Resolution Error
    # --------------------------------------------------

    except socket.gaierror as error:

        log_error(
            f"Unable to resolve hostname: {error}"
        )

        return {
            "success": False,

            "status": "Unavailable",

            "sslValid": None,

            "protocol": "Unknown",

            "certificate": False,

            "error": {
                "code": "SSL_DNS_ERROR",
                "message":
                    "Unable to resolve the website hostname."
            }
        }

    # --------------------------------------------------
    # Unexpected Exception
    # --------------------------------------------------

    except Exception as error:

        log_error(
            f"Unexpected SSL Error: {error}"
        )

        return {
            "success": False,

            "status": "Unavailable",

            "sslValid": None,

            "protocol": "Unknown",

            "certificate": False,

            "error": {
                "code": "SSL_CHECK_ERROR",
                "message":
                    "SSL/TLS validation could not be completed."
            }
        }

