from netconf_xml_builder import netconf_hello, netconf_commit, pretty_xml, \
    netconf_close_session, netconf_get_config, netconf_get, netconf_delimiter, \
    make_netconf_message, netconf_xml

# Generate a <hello> message
hello_elem = netconf_hello()
print("NETCONF <hello> message:")
print(pretty_xml(hello_elem))

# Generate a <commit> message with persist
commit_elem = netconf_commit(persist="my-persist-id")
print("\nNETCONF <commit> message with persist:")
print(pretty_xml(commit_elem))

# Generate a <close-session> message
close_elem = netconf_close_session(message_id=42)
print("\nNETCONF <close-session> message:")
print(pretty_xml(close_elem))

# Generate a <get-config> message
get_config_elem = netconf_get_config()
print("\nNETCONF <get-config> message:")
print(pretty_xml(get_config_elem))


# Generate a <get> message with a filter

def filter_fun(parent):
    from xml.etree.ElementTree import Element
    f = Element('filter')
    f.text = 'interface-config'
    parent.append(f)


get_elem = netconf_get(filter_fun=filter_fun)
print("\nNETCONF <get> message with filter:")
print(pretty_xml(get_elem))

# Show NETCONF message delimiter
print("\nNETCONF delimiter:")
print(repr(netconf_delimiter()))

# Show how to use make_netconf_message to combine messages
messages = [hello_elem, commit_elem, close_elem]
print("\nCombined NETCONF messages:")
print(make_netconf_message(messages))


# Example of using the netconf_xml decorator directly
def custom_operation(nce):
    from xml.etree.ElementTree import SubElement
    SubElement(nce, "custom-op").text = "custom-value"
    return nce


custom_op = netconf_xml("rpc")(custom_operation)
custom_elem = custom_op()
print("\nCustom NETCONF operation:")
print(pretty_xml(custom_elem))


# Example of using the netconf_xml decorator directly with @netconf_xml

@netconf_xml()
def another_custom_rpc(nce, foo, bar):
    from xml.etree.ElementTree import SubElement
    op = SubElement(nce, "another-custom-op")
    SubElement(op, "foo").text = str(foo)
    SubElement(op, "bar").text = str(bar)
    return nce


custom_elem3 = another_custom_rpc(foo="world", bar=456)
print("\nCustom NETCONF operation using @netconf_xml:")
print(pretty_xml(custom_elem3))


# Example of using the netconf_xml decorator directly with @netconf_xml and a custom tag

@netconf_xml(tag="my-rpc-tag")
def tagged_custom_rpc(nce, foo, bar):
    from xml.etree.ElementTree import SubElement
    op = SubElement(nce, "tagged-custom-op")
    SubElement(op, "foo").text = str(foo)
    SubElement(op, "bar").text = str(bar)
    return nce


custom_elem4 = tagged_custom_rpc(foo="tagged", bar=789)
print("\nCustom NETCONF operation using @netconf_xml(tag='my-rpc-tag'):")
print(pretty_xml(custom_elem4))
