from lxml import etree


def validate_ubl_xml(xml: bytes) -> list[str]:
    """Check well-formed XML. TODO: connect official Peppol XSD and Schematron rules."""
    try:
        etree.fromstring(xml)
    except etree.XMLSyntaxError as exc:
        return [str(exc)]
    return []
