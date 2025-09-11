"""Top-level package for Python NETCONF XML Builder library."""

__author__ = """Michal Novák"""
__email__ = 'it.novakmi@gmail.com'
__version__ = '0.1.0'

from .netconf_xml_builder import netconf_hello, netconf_commit, pretty_xml, \
    netconf_close_session, netconf_get_config, netconf_get, netconf_delimiter, \
    make_netconf_message, netconf_xml

__all__ = [
    "netconf_hello",
    "netconf_commit",
    "pretty_xml",
    "netconf_close_session",
    "netconf_get_config",
    "netconf_get",
    "netconf_delimiter",
    "make_netconf_message",
    "netconf_xml",
]
