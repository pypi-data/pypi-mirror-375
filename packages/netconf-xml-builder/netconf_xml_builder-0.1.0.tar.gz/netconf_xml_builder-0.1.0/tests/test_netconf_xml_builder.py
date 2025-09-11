import logging
from xml.etree.ElementTree import Element
from netconf_xml_builder import netconf_xml_builder

log = logging.getLogger(__name__)


def test_netconf_hello():
    elem = netconf_xml_builder.netconf_hello()
    xml_str = netconf_xml_builder.pretty_xml(elem)
    assert '<hello' in xml_str
    assert '<capabilities>' in xml_str
    assert 'urn:ietf:params:netconf:base:1.0' in xml_str


def test_netconf_close_session():
    elem = netconf_xml_builder.netconf_close_session(message_id=123)
    xml_str = netconf_xml_builder.pretty_xml(elem)
    assert '<close-session' in xml_str
    assert 'message-id="123"' in xml_str


def test_netconf_commit():
    elem = netconf_xml_builder.netconf_commit(persist='abc')
    xml_str = netconf_xml_builder.pretty_xml(elem)
    assert '<commit>' in xml_str
    assert '<persist>abc</persist>' in xml_str
    elem2 = netconf_xml_builder.netconf_commit(persist_id='xyz')
    xml_str2 = netconf_xml_builder.pretty_xml(elem2)
    assert '<persist-id>xyz</persist-id>' in xml_str2


def test_netconf_get_config():
    elem = netconf_xml_builder.netconf_get_config()
    xml_str = netconf_xml_builder.pretty_xml(elem)
    assert '<get-config>' in xml_str
    assert '<running/>' in xml_str or '<running></running>' in xml_str


def test_netconf_get_with_filter():
    def filter_fun(parent: Element):
        f = Element('filter')
        f.text = 'test'
        parent.append(f)
    elem = netconf_xml_builder.netconf_get(filter_fun=filter_fun)
    xml_str = netconf_xml_builder.pretty_xml(elem)
    assert '<get>' in xml_str
    assert '<filter>test</filter>' in xml_str


def test_netconf_delimiter():
    delim = netconf_xml_builder.netconf_delimiter()
    assert delim == ']]>]]>\n'


def test_make_netconf_message():
    elem1 = netconf_xml_builder.netconf_hello()
    elem2 = netconf_xml_builder.netconf_close_session()
    msg = netconf_xml_builder.make_netconf_message([elem1, elem2])
    assert msg.count(']]>]]>') == 2
    assert '<hello' in msg and '<close-session' in msg
