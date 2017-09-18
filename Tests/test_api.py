import datetime
import json
import re
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

import pytest

import fapy.api as api
import fapy.server as server
import auth


class CheckResults(object):

    @staticmethod
    def frame(frame, test_data):
        CheckResults.attr(frame.attr)
        assert isinstance(frame, server.Dframe)
        assert frame.attr["frame_type"] == test_data["frame_type"]
        assert frame.shape == test_data["shape"]
        assert frame.index.min() == 0
        assert frame.index.max() == (test_data["shape"][0] - 1)
        assert frame.index.is_monotonic_increasing
        col, row, value = test_data["spotcheck"]
        assert frame[col][row] == value
        json.loads(frame.attr["text"])  # Verify that "text" is valid JSON text.

    @staticmethod
    def dict(dictionary, test_data):
        CheckResults.attr(dictionary)
        assert isinstance(dictionary, dict)
        assert dictionary["frame_type"] == test_data["frame_type"]
        if dictionary["text_format"] == "json":
            return json.loads(dictionary["text"])  # Verify "text" valid JSON.
        elif dictionary["text_format"] == "xml":
            return ET.fromstring(dictionary["text"])  # Verify "text valid XML.
        else:
            pytest.fail("dict['text_format'] invalid. Should be 'xml' or "
                        "'json'. Instead contains " + dictionary["text_format"])

    @staticmethod
    def attr(attr):
        assert attr["code"] == 200
        assert server.httpdate_to_datetime(attr["Last-Modified"])
        assert server.httpdate_to_datetime(attr["time_downloaded"], False)
        assert attr["mod_since"] is None
        assert attr["only_mod_since"] is None
        assert re.match("https://frc-api.firstinspires.org/v2.0/20",
                        attr["url"]) is not None
        CheckResults.local(attr)

    @staticmethod
    def local(attr):
        assert (attr["local_data"] is True) or (attr["local_data"] is False)
        if attr["local_data"]:
            assert server.httpdate_to_datetime(attr["local_time"], False)
            assert re.match("https://frc-api.firstinspires.org/v2.0/20",
                            attr["requested_url"]) is not None
        else:
            assert attr["local_time"] is None
            assert attr["requested_url"] == attr["url"]

    @staticmethod
    def mod_since(result, mod_since):
        if isinstance(result, server.Dframe):
            attr = result.attr
            assert result["If-Modified-Since"][0] == mod_since
        else:
            attr = result
        assert attr["text"] is None
        assert attr["code"] == 304
        assert attr["mod_since"] == mod_since

    @staticmethod
    def only_mod_since(result, only_mod_since):
        if isinstance(result, server.Dframe):
            attr = result.attr
            assert result["FMS-OnlyModifiedSince"][0] == only_mod_since
        else:
            attr = result
        assert attr["text"] is None
        assert attr["code"] == 304
        assert attr["only_mod_since"] == only_mod_since


class TestStatus(object):

    def test_status(self):
        sn = api.Session(auth.username, auth.key, season='2017')
        status = api.get_status(sn)
        tdata = {"frame_type": "status", "shape": (1, 3),
                 "spotcheck": ("name", 0, "FIRST ROBOTICS COMPETITION API")}
        CheckResults.frame(status, tdata)


class TestSeason(object):

    def test_2017(self, session):
        sn = api.Session(auth.username, auth.key, season='2017')
        season = api.get_season(sn)
        tdata = {"frame_type": "season", "shape": (2, 8),
                 "spotcheck": ("teamCount", 0, 3372)}
        CheckResults.frame(season, tdata)

    def test_2016(self):
        sn = api.Session(auth.username, auth.key, season='2016')
        season = api.get_season(sn)
        tdata = {"frame_type": "season", "shape": (1, 8),
                 "spotcheck": ("teamCount", 0, 3140)}
        CheckResults.frame(season, tdata)

    def test_xml(self):
        sn = api.Session(auth.username, auth.key, season='2017')
        sn.data_format = "xml"
        season = api.get_season(sn)
        tdata = {"frame_type": "season"}
        CheckResults.dict(season, tdata)

    def test_local(self):
        sn = api.Session(auth.username, auth.key, season='2017')
        sn.source = "local"
        season = api.get_season(sn)
        tdata = {"frame_type": "season", "shape": (2, 8),
                 "spotcheck": ("teamCount", 0, 3372)}
        CheckResults.frame(season, tdata)


class TestDistricts(object):

    def test_df(self):
        sn = api.Session(auth.username, auth.key, season='2017')
        districts = api.get_districts(sn)
        tdata = {"frame_type": "districts", "shape": (10, 3),
                 "spotcheck": ("code", 0, "IN")}
        CheckResults.frame(districts, tdata)

        # Test no data and 304 code returned when mod_since used.
        lmod = server.httpdate_addsec(districts.attr["Last-Modified"], True)
        dist2 = api.get_districts(sn, mod_since=lmod)
        CheckResults.mod_since(dist2, lmod)

        # Test no data and 304 code returned when only_mod_since used.
        dist3 = api.get_districts(sn, only_mod_since=lmod)
        CheckResults.only_mod_since(dist3, lmod)


class TestEvents(object):

    def test_df(self):
        sn = api.Session(auth.username, auth.key, season='2017')
        events = api.get_events(sn, district="PNW")
        tdata = {"frame_type": "events", "shape": (10, 15),
                 "spotcheck": ("code", 0, "ORLAK")}
        CheckResults.frame(events, tdata)

        # Test no data and 304 code returned when mod_since used.
        lmod = server.httpdate_addsec(events.attr["Last-Modified"], True)
        events2 = api.get_events(sn, district="PNW", mod_since=lmod)
        CheckResults.mod_since(events2, lmod)

        # Test no data and 304 code returned when only_mod_since used.
        events3 = api.get_events(sn, district="PNW", only_mod_since=lmod)
        CheckResults.only_mod_since(events3, lmod)


class TestTeams(object):

    def test_df(self):
        sn = api.Session(auth.username, auth.key, season='2017')
        teams = api.get_teams(sn, district="PNW")
        tdata = {"frame_type": "teams", "shape": (155, 16),
                 "spotcheck": ("teamNumber", 13, 1318)}
        CheckResults.frame(teams, tdata)

        lmod = server.httpdate_addsec(teams.attr["Last-Modified"], True)
        teams2 = api.get_teams(sn, district="PNW", mod_since=lmod)
        CheckResults.mod_since(teams2, lmod)

    def test_page(self):
        sn = api.Session(auth.username, auth.key, season='2017')
        teams = api.get_teams(sn, district="PNW", page="2")
        tdata = {"frame_type": "teams", "shape": (65, 16),
                 "spotcheck": ("nameShort", 64, "Aluminati")}
        CheckResults.frame(teams, tdata)

        lmod = server.httpdate_addsec(teams.attr["Last-Modified"], True)
        teams2 = api.get_teams(sn, district="PNW", page="2",
                               only_mod_since=lmod)
        CheckResults.only_mod_since(teams2, lmod)


class TestSchedule(object):

    def test_df(self):
        sn = api.Session(auth.username, auth.key, season='2017')
        schedule = api.get_schedule(sn, event="TURING", team="1318")
        tdata = {"frame_type": "schedule", "shape": (60, 8),
                 "spotcheck": ("teamNumber", 3, 1318)}
        CheckResults.frame(schedule, tdata)

