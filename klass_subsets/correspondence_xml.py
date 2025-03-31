import xml.etree.ElementTree as ET


def generate_correspondence_xml(elements: list[dict], filename: str) -> None:
    """Generates the xml file for input to klass."""
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
        "Korrespondansetabell",
        {
            "xmlns": "http://klass.ssb.no/correspondenceTable",
            "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "xsi:schemaLocation": "http://klass.ssb.no/correspondenceTable https://i.ssb.no/klass/admin/schemas/correspondenceTable.xsd",
        },
    )

    # Create child elements
    for elem in elements:
        element = ET.SubElement(root, "Korrespondanse")
        ET.SubElement(element, "kilde_kode").text = elem["current_code"]
        ET.SubElement(element, "kilde_tittel").text = elem["current_nb"]
        ET.SubElement(element, "mål_kode").text = elem["previous_code"]
        ET.SubElement(element, "mål_tittel").text = elem["previous_nb"]

    # Write XML to file with proper indentation
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ", level=0)  # Indent with 2 spaces
    tree.write(filename, encoding="utf-8", xml_declaration=True)
