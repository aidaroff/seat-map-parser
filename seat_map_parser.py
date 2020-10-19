#!/usr/bin/env python3.6

import json

from typing import Optional

import xml.etree.ElementTree as ET


NS = 'http://www.opentravel.org/OTA/2003/05/common/'


def _generate_match_param(tag: str) -> str:
    return ".//{%s}%s" % (NS, tag)


def _get_attr_value_in_child_tag(parent_tag: ET.Element, child_tag_str: str, attr: str) -> Optional[str]:
    tag: ET.Element = parent_tag.find(_generate_match_param(child_tag_str))
    if tag is not None:
        return tag.attrib.get(attr)


def _get_seat_map_details(root: ET.Element) -> ET.Element:
    match = _generate_match_param("SeatMapDetails")
    return root.find(match)


def _get_flight_segment_info(root: ET.Element) -> ET.Element:
    match = _generate_match_param("FlightSegmentInfo")
    return root.find(match)


def _parse_seat_map_details(seat_map_details: ET.Element) -> dict:
    def _get_seat_pricing(seat: ET.Element) -> dict:
        service = seat.find(_generate_match_param("Service"))
        if not service:
            return None
        fee = service.find(_generate_match_param("Fee"))
        if fee is None:
            return None
        pricing_info = {
            "fee": {
                "amount": fee.attrib.get("Amount"),
                "currency": fee.attrib.get("CurrencyCode"),
            },
            "taxes": None,
        }
        taxes = fee.find(_generate_match_param("Taxes"))
        if taxes is None:
            return pricing_info
        pricing_info.update({
            "taxes": {
                "amount": taxes.attrib.get("Amount"),
                "currency": taxes.attrib.get("CurrencyCode"),
            },
        })
        return pricing_info

    def _get_seat_type(features: ET.Element) -> str:
        for feature in features:
            extension = feature.attrib.get("extension")
            if extension == "Lavatory":
                return "Bathroom"
        return "Seat"


    def _parse_seat_row(seat_row: ET.Element) -> dict:
        parsed_seats = []
        cabin_type = seat_row.attrib.get("CabinType")
        seats = seat_row.findall(_generate_match_param("SeatInfo"))
        for seat in seats:
            features: ET.Element = seat.findall(_generate_match_param("Features"))
            availability = _get_attr_value_in_child_tag(parent_tag=seat, child_tag_str="Summary", attr="AvailableInd")
            parsed_seat = {
                "cabin": cabin_type.lower() if cabin_type is not None else None,
                "number": _get_attr_value_in_child_tag(parent_tag=seat, child_tag_str="Summary", attr="SeatNumber"),
                "price": _get_seat_pricing(seat),
                "available": True if availability == "true" else False,
                "type": _get_seat_type(features),
            }
            parsed_seats.append(parsed_seat)
        
        return parsed_seats

    resulting_seat_rows = []
    for cabin_class in seat_map_details:
        for seat_row in cabin_class:
            resulting_seat_rows.extend(_parse_seat_row(seat_row))

    return resulting_seat_rows


def _parse_flight_segment_info(flight_seg_info: ET.Element) -> dict:
    def _get_departure_time(flight_seg_info) -> str:
        return flight_seg_info.attrib.get("DepartureDateTime")

    def _get_flight_number(flight_seg_info) -> str:
        return flight_seg_info.attrib.get("FlightNumber")

    return {
        "departure": {
            "airport": _get_attr_value_in_child_tag(
                parent_tag=flight_seg_info, child_tag_str="DepartureAirport", attr="LocationCode"
            ),
            "datetime": _get_departure_time(flight_seg_info),
        },
        "arrival": {
            "airport": _get_attr_value_in_child_tag(
                parent_tag=flight_seg_info, child_tag_str="ArrivalAirport", attr="LocationCode"
            ),
        },
        "equipment": _get_attr_value_in_child_tag(
            parent_tag=flight_seg_info, child_tag_str="Equipment", attr="AirEquipType"
        ),
    }

def parse_seat_map_response(root: ET.Element) -> dict:
    parsed_flight_seg_info = {}
    flight_seg_info: ET.Element = _get_flight_segment_info(root)
    if flight_seg_info is not None:
        parsed_flight_seg_info: dict = _parse_flight_segment_info(flight_seg_info)

    seat_map_details: ET.Element = _get_seat_map_details(root)
    parsed_response = {
        "seats": _parse_seat_map_details(seat_map_details),
        "segment": parsed_flight_seg_info,
    }

    return parsed_response
