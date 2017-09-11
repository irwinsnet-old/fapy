import datetime
import json
import re
import xml.etree.ElementTree as ET

import pytest

import fapy.api as api
import fapy.server as server

import auth


@pytest.fixture
def session():
    return api.Session(auth.username, auth.key, season=2017)


def check_frame(frame, test_data):
    check_attr(frame.attr)
    assert isinstance(frame, server.Dframe)
    assert frame.attr["frame_type"] == test_data["frame_type"]
    assert frame.shape == test_data["shape"]
    col, row, value = test_data["spotcheck"]
    assert frame[col][row] == value
    json.loads(frame.attr["text"])  # Verify that "text" is valid JSON text.


def check_dict(dictionary, test_data):
    check_attr(dictionary)
    assert isinstance(dictionary, dict)
    assert dictionary["frame_type"] == test_data["frame_type"]
    if dictionary["text_format"] == "json":
        return json.loads(dictionary["text"])  # Verify "text" is valid JSON.
    elif dictionary["text_format"] == "xml":
        return ET.fromstring(dictionary["text"]) # Verify "text is valid XML.
    else:
        pytest.fail("dict['text_format'] invalid. Should be 'xml' or 'json'."
                    "Instead contains " + dictionary["text_format"])


def check_attr(attr):
    assert attr["code"] == 200
    assert server.httpdate_to_datetime(attr["Last-Modified"])
    assert server.httpdate_to_datetime(attr["time_downloaded"], False)
    # todo (stacy.irwin) revise to check local data.

    assert attr["mod_since"] is None
    assert attr["only_mod_since"] is None
    assert re.match("https://frc-api.firstinspires.org/v2.0/20",
                    attr["url"]) is not None
    check_local(attr)


def check_local(attr):
    assert (attr["local_data"] is True) or (attr["local_data"] is False)
    if attr["local_data"]:
        assert server.httpdate_to_datetime(attr["local_time"], False)
        assert re.match("https://frc-api.firstinspires.org/v2.0/20",
                    attr["requested_url"]) is not None
    else:
        assert attr["local_time"] is None
        assert attr["requested_url"] == attr["url"]


class TestSeason(object):

    def test_2017(self, session):
        season = api.get_season(session)
        tdata = {"frame_type": "season", "shape": (2, 8),
                 "spotcheck": ("teamCount", 0, 3372)}
        check_frame(season, tdata)

    def test_2016(self, session):
        session.season = 2016
        season = api.get_season(session)
        tdata = {"frame_type": "season", "shape": (1, 8),
                 "spotcheck": ("teamCount", 0, 3140)}
        check_frame(season, tdata)

    def test_xml(self, session):
        session.data_format = "xml"
        season = api.get_season(session)
        tdata = {"frame_type": "season"}
        check_dict(season, tdata)

    def test_local(self, session):
        session.source = "local"
        season = api.get_season(session)
        tdata = {"frame_type": "season", "shape": (2, 8),
                 "spotcheck": ("teamCount", 0, 3372)}
        check_frame(season, tdata)
        assert isinstance(season, server.Dframe)


class TestDistricts(object):

    def test_df(self):
        sn = api.Session(auth.username, auth.key, season=2017)
        districts = api.get_districts(sn)
        assert isinstance(districts, server.Dframe)
        assert districts.attr["frame_type"] == "districts"
        assert districts.shape == (10, 3)
        assert districts["code"][0] == "IN"


class TestEvents(object):

    def test_df(self):
        sn = api.Session(auth.username, auth.key, season=2017)
        events = api.get_events(sn, district="PNW")
        assert isinstance(events, server.Dframe)
        assert events.attr["frame_type"] == "events"
        assert events.shape == (10, 15)
        assert events["code"][0] == "ORLAK"


class TestStatus(object):

    def test_df(self):
        sn = api.Session(auth.username, auth.key, season=2017)
        status = api.get_status(sn)
        assert isinstance(status, server.Dframe)
        assert status.attr["frame_type"] == "status"
        assert status.shape == (1, 3)
        assert status["version"][0] == 2


class TestTeams(object):

    def test_df(self):
        sn = api.Session(auth.username, auth.key)
        teams = api.get_teams(sn, district="PNW")
        assert isinstance(teams, server.Dframe)
        assert teams.attr["frame_type"] == "teams"
        assert teams.shape == (155, 16)
        assert teams["teamNumber"].iloc[0] == 360


class TestSchedule(object):

    def test_df(self):
        sn = api.Session(auth.username, auth.key, season='2017')
        schedule = api.get_schedule(sn, event="PNCMP")
        assert isinstance(schedule, server.Dframe)
        assert schedule.attr["frame_type"] == "schedule"
        assert list(schedule) == ['station', 'surrogate', 'teamNumber',
                                  'matchNumber', 'description', 'field',
                                  'startTime', 'tournamentLevel']
        assert schedule.shape == (768, 8)
        assert schedule["teamNumber"].iloc[0] == 2910


class TestModifiedSince(object):

    def test_modified_since(self):
        sn = api.Session(auth.username, auth.key, data_format="json")
        dist = api.get_districts(sn)
        last_mod = dist["Last-Modified"]
        print()
        print(last_mod)
        dtm = server.httpdate_to_datetime(last_mod)
        dtm_new = dtm + datetime.timedelta(seconds=1)
        last_mod_new = server.datetime_to_httpdate(dtm_new)
        dist_lm = api.get_districts(sn, mod_since=last_mod_new)
        assert dist_lm["text"] is None
        print(dist_lm["mod_since"])

