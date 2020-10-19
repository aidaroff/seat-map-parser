import json
import xml.etree.ElementTree as ET

from seat_map_parser import parse_seat_map_response


if __name__ == "__main__":
    tree = ET.parse('OTA_AirSeatMapRS.xml')
    response: dict = parse_seat_map_response(tree.getroot())
    with open('OTA_AirSeatMapRS.json', 'w') as f:
        f.write(json.dumps(response, indent=4))
