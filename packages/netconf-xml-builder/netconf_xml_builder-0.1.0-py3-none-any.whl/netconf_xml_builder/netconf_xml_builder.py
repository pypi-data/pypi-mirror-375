from xml.etree.ElementTree import Element, Comment, SubElement, tostring
from typing import Callable, Optional, Any


def netconf_xml(tag: str = "rpc") -> Callable:
    """
    Decorator to wrap NETCONF XML operations with a root tag and namespace.
    Adds optional message-id and a comment.
    """

    def netconf_dec(func: Callable) -> Callable:
        def netconf_wrap(*args, **kwargs) -> Element:
            atrs = {"xmlns": "urn:ietf:params:xml:ns:netconf:base:1.0"}
            if "message_id" in kwargs:
                atrs["message-id"] = str(kwargs["message_id"])
            nce = Element(tag, atrs)
            nce.append(Comment("This part is generated"))
            # Only pass arguments relevant to the wrapped function
            func_kwargs = {k: v for k, v in kwargs.items() if k != "message_id"}
            return func(nce, *args, **func_kwargs)

        return netconf_wrap

    return netconf_dec


@netconf_xml(tag="hello")
def netconf_hello(nce: Element) -> Element:
    """Generate NETCONF <hello> message."""
    cap = SubElement(SubElement(nce, "capabilities"), "capability")
    cap.text = "urn:ietf:params:netconf:base:1.0"
    return nce


@netconf_xml()
def netconf_close_session(nce: Element,
                          message_id: Optional[Any] = None) -> Element:
    """Generate NETCONF <close-session> message."""
    SubElement(nce, "close-session")
    return nce


@netconf_xml()
def netconf_commit(nce: Element, message_id: Optional[Any] = None,
                   persist: Optional[Any] = None,
                   persist_id: Optional[Any] = None) -> Element:
    """Generate NETCONF <commit> message with optional persist/persist-id."""
    commit = SubElement(nce, "commit")
    if persist is not None:
        SubElement(commit, "confirmed")
        SubElement(commit, "persist").text = str(persist)
    elif persist_id is not None:
        SubElement(commit, "persist-id").text = str(persist_id)
    return nce


@netconf_xml()
def netconf_get_config(nce: Element,
                       message_id: Optional[Any] = None) -> Element:
    """Generate NETCONF <get-config> message for running config."""
    SubElement(SubElement(SubElement(nce, "get-config"), "source"), "running")
    return nce


@netconf_xml()
def netconf_get(nce: Element, message_id: Optional[Any] = None,
                filter_fun: Optional[Callable] = None) -> Element:
    """Generate NETCONF <get> message, optionally with a filter function."""
    get = SubElement(nce, "get")
    if filter_fun is not None:
        filter_fun(get)
    return nce


# ## Netconf related
def netconf_delimiter():
    return "]]>]]>\n"


def make_netconf_message(message_list):
    """Return a pretty-printed XML string for the Element.
        http://pymotw.com/2/xml/etree/ElementTree/create.html
    """
    netconf = ""
    for m in message_list:
        netconf += pretty_xml(m)
        netconf += netconf_delimiter()
    return netconf


def pretty_xml(element: Element) -> str:
    """Return a pretty-printed XML string for the Element."""
    import xml.dom.minidom
    rough_string = tostring(element, 'utf-8')
    reparsed = xml.dom.minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
