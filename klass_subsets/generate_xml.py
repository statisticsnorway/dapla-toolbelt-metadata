import xml.etree.ElementTree as ET


def generate_xml(elements, filename):
    # Define namespace
    ns = {
        "": "http://klass.ssb.no/version",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    # Register namespace
    ET.register_namespace("", ns[""])
    ET.register_namespace("xsi", ns["xsi"])

    # Create root element with fixed attributes
    root = ET.Element(
        "versjon",
        {
            "xmlns": "http://klass.ssb.no/version",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://klass.ssb.no/version https://i.ssb.no/klass/admin/schemas/version.xsd",
        },
    )

    # Create child elements
    for elem in elements:
        element = ET.SubElement(root, "element")
        ET.SubElement(element, "kode").text = elem["code"]
        ET.SubElement(element, "forelder").text = ""
        ET.SubElement(element, "navn_bokmål").text = elem["nb"]
        ET.SubElement(element, "navn_nynorsk").text = elem["nn"]
        ET.SubElement(element, "navn_engelsk").text = elem["en"]
        ET.SubElement(element, "kortnavn_bokmål").text = ""
        ET.SubElement(element, "kortnavn_nynorsk").text = ""
        ET.SubElement(element, "kortnavn_engelsk").text = ""
        ET.SubElement(element, "noter_bokmål").text = ""
        ET.SubElement(element, "noter_nynorsk").text = ""
        ET.SubElement(element, "noter_engelsk").text = ""

        if elem["valid_until"] is not None:
            ET.SubElement(element, "gyldig_til").text = elem["valid_until"]
        else:
            ET.SubElement(element, "gyldig_til").text = ""
        ET.SubElement(element, "gyldig_fra").text = elem["valid_from"]

    # Write XML to file with proper indentation
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)  # Indent with 2 spaces
    tree.write(filename, encoding="utf-8", xml_declaration=True)
