import datetime

import fapy.api as api
import fapy.server as server

import auth


class TestSeason(object):

    def test_2017(self):
        sn = api.Session(auth.username, auth.key, season=2017)
        season = api.get_season(sn)
        assert season.attr["code"] == 200
        assert isinstance(season, server.Dframe)
        assert season.attr["frame_type"] == "season"
        assert season.shape == (2, 8)
        assert season["teamCount"][0] == 3372

    def test_2016(self):
        sn = api.Session(auth.username, auth.key, season=2016)
        season = api.get_season(sn)
        assert isinstance(season, server.Dframe)
        assert season.attr["frame_type"] == "season"
        assert season.shape == (1, 8)
        assert season["teamCount"][0] == 3140

    def test_xml(self):
        sn = api.Session(auth.username, auth.key, data_format="xml")
        season = api.get_season(sn)
        assert isinstance(season, dict)
        assert season["frame_type"] == "season"
        # try:
        #     xml = ET.fromstring(season_summary["response_text"])
        # except ET.ParseError:
        #     assert (False, "XML parsing error, " +
        #             "season_summary did not return valid XML.")
        # else:
        #     pass
        # finally:
        #     pass

    def test_local(self):
        sn = api.Session(auth.username, auth.key, season=2017,
                         source="local")
        season = api.get_season(sn)
        assert isinstance(season, server.Dframe)
        assert season.attr["frame_type"] == "season"
        assert season.shape == (2, 8)
        assert season["teamCount"][0] == 3372
        assert season.attr["local_data"]
        assert season.attr["local_time"] is not None


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

