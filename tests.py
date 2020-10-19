import json
import xml.etree.ElementTree as ET

from seat_map_parser import parse_seat_map_response


if __name__ == "__main__":
    tree = ET.parse('OTA_AirSeatMapRS.xml')
    response: dict = parse_seat_map_response(tree.getroot())
    print("Running a set of assert checks...")
    assert "segment" in response
    assert "seats" in response

    assert len(response["seats"]) == 170
    assert response["segment"]["departure"]["airport"] == "LAS"
    assert response["segment"]["arrival"]["airport"] == "IAH"
    assert response["segment"]["equipment"] == "739"

    seats_with_fees = len([seat for seat in response["seats"] if seat["price"] is not None])
    assert seats_with_fees == 104

    available_seats = len([seat for seat in response["seats"] if seat["available"] == True])
    assert available_seats == 104
    print("Done... Pass")
