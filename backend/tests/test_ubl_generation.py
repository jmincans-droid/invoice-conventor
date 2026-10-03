from lxml import etree

from app.validation.ubl_validator import validate_ubl_xml
from app.xml.ubl_invoice import generate_ubl_invoice


def test_ubl_is_well_formed_and_contains_core_values(valmieras) -> None:
    xml = generate_ubl_invoice(valmieras)
    assert validate_ubl_xml(xml) == []
    root = etree.fromstring(xml)
    assert root.xpath("string(//*[local-name()='ID'][1])") == "VGS1"
    assert root.xpath("count(//*[local-name()='InvoiceLine'])") == 1.0
    endpoints = root.xpath("//*[local-name()='EndpointID']")
    assert [endpoint.text for endpoint in endpoints] == ["40008249801", "40203365911"]
    assert all(endpoint.get("schemeID") == "0218" for endpoint in endpoints)
