"""
HTTPS Checker Module

This module checks whether a website
uses the HTTPS protocol.
"""


def check_https(url):
    """
    Check whether the website uses HTTPS.

    Parameters
    ----------
    url : str
        Website URL.

    Returns
    -------
    dict
        {
            "https": bool
        }
    """

    if not isinstance(url, str):

        return {

            "https": False

        }

    url = url.strip()

    return {

        "https": url.lower().startswith("https://")

    }