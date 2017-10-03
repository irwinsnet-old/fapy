"""Functions for downloading FRC event data from FIRST API.

All functions for downloading FIRST API data require an instance of
the Session class, which contains the account username, authorization
key, competition season, etc. The functions in this module return
either an instance of fapy.http.FIRSTDf, which is a subclassed pandas
dataframe with additional metadata, or an instance of
fapy.http.FIRSTResponse, which acts like a Python dictionary.

License:
    GNU General Public License v3.0

Version:
    0.0.1

Copyright 2017, Stacy Irwin
"""
import collections
import datetime
import warnings

import pandas.io.json

import fapy.server as server


def _send_request(session, cmd, args=None, mod_since=None,
                  only_mod_since=None):
    """

    Args:
        session:
        cmd:
        args: A Python dictionary.
        mod_since:
        only_mod_since:

    Returns:

    """
    url = server.build_url(session, cmd, args)
    if session.source == "local":
        response = server.send_local_request(session, url, cmd)
    else:
        response = server.send_http_request(session, url, cmd, mod_since,
                                            only_mod_since)
    if session.data_format == "dataframe":
        return server.Dframe(response)
    else:
        return response


def get_status(session):
    """
    Retrieves server status.

    Args:
        session: An instance of fapy.classes.Session that contains
            a valid username and authorization key.

    Returns:
        If session.data_format == "json" or "xml", returns a Python
        dictionary object containing the response text and additional
        metadata. If session.data_format == "dataframe", returns an instances
        of fapy.server.Dframe, which is a Pandas dataframe with
        an additional `attr` property that contains a Python dictionary
        with additional metadata.
    """
    return _send_request(session, "status", None)


def get_season(session):
    """ Retrieves information on an FRC competition season_summary.

    Args:
        session: An instance of fapy.get.Session that contains
            a valid username and authorization key.

    Returns:
        If Session.data_format == "json" or "xml", returns a Python
        dictionary object containing the response text and additional
        metadata. If Session.data_format == "dataframe", returns an instances
        of fapy.http.FirstDF, which is a Pandas dataframe with
        an additional `attr` property that contains a Python dictionary
        with additional metadata.
    """
    return _send_request(session, "season", None)


def get_districts(session, mod_since=None, only_mod_since=None):
    """
    Retrieves information on FIRST districts.

    Args:
        session: An instance of fapy.classes.Session that contains
            a valid username and authorization key.
        mod_since: A string containing an HTTP formatted date and time.
            Causes function to return None if no changes have been
            made to the requested data since the date and time provided.
            Optional.
        only_mod_since: A string containing an HTTP formatted date and
            time. Causes function to only return data that has
            changed since the date and time provided. Optional.

    Returns:
        If session.data_format == "json" or "xml", returns a Python
        dictionary object containing the response text and additional
        metadata. If session.data_format == "dataframe", returns an instances
        of fapy.classes.http.FirstDf, which is a Pandas dataframe with
        an additional `attr` property that contains a Python dictionary
        with additional metadata.
    """
    return _send_request(session, "districts", None, mod_since,
                         only_mod_since)


def get_events(session,  # pylint: disable=too-many-arguments
               event=None, team=None, district=None,
               exclude_district=None, mod_since=None,
               only_mod_since=None):
    """
    Retrieves information on one or more FRC competitions.

    Args:
        session: An instance of fapy.classes.Session that contains
            a valid username and authorization key.
        event: A string containing a FIRST event code.
        team: The four digit FRC team number as an integer.
        district: A string containing the FIRST district code, such as
            "PNW" for the Pacific Northwest district. Results will be
            filtered to the events occurring in that district. Use
            `districts()` to retrieve all district codes.
        exclude_district: A Boolean value. If True, filters results to
            events that are not affiliated with a district.
        mod_since: A string containing an HTTP formatted date and time.
            Causes function to return None if no changes have been
            made to the requested data since the date and time provided.
            Optional.
        only_mod_since: A string containing an HTTP formatted date and
            time. Causes function to only return data that has
            changed since the date and time provided. Optional.

    Returns:
        If session.data_format == "json" or "xml", returns a Python
        dictionary object containing the response text and additional
        metadata. If session.data_format == "dataframe", returns an instances
        of fapy.server.Dframe, which is a Pandas dataframe with
        an additional `attr` property that contains a Python dictionary
        with additional metadata.

    Raises:
        fapy.Classes.ArgumentError:
            * If the `event` argument is specified and any other
              argument is specified in addition to `event` (i.e.,
              if `event` is specified, no other arguments should be
              used).
            * If both the `district` and `exclude_district` arguments
              are specified (i.e., use one or the other but not both).
    """

    # Check for un-allowed combinations of arguments
    if (event is not None and (team is not None or district is not None
                               or exclude_district is not None)):
        raise server.ArgumentError("If you specify an event, you "
                                   "cannot specify any other arguments.")
    if district is not None and exclude_district is not None:
        raise server.ArgumentError(
            "You cannot specify both the district and"
            "exclude_district arguments.")

    event_args = {"eventCode": event, "teamNumber": team,
                  "districtCode": district,
                  "excludeDistrict": exclude_district}
    return _send_request(session, "events", event_args, mod_since,
                         only_mod_since)


def get_teams(session,  # pylint: disable=too-many-arguments
              team=None, event=None, district=None, state=None,
              page=None, mod_since=None, only_mod_since=None):
    """Retrieves FRC teams from FIRST API Server.

    Args:
        session: An instance of fapy.classes.Session that contains
            a valid username and authorization key.
        team: FRC team number as a string. If listed, function will
            return data only for that team. Optional.
        event: A string containing the FIRST API event code. If
            included, function will return only teams that are
            competing in that event. Use fapy.api.get_events to lookup
            event codes. Optional.
        district: A string containing the FIRST API district code. If
            included, function will only return teams that are
            competing in that event. Optional.
        state: A string containing the name of the U.S. state, spelled
            out. If included, function will only return teams that are
            located in that state.
        page: A string containing the requested page number. The FIRST
            API splits long lists of teams into several pages and only
            returns one page at a time. For XML and JSON data, if page
            is omitted, the FIRST API and this function will return
            only the first page of data. Users can retrieve subsequent
            pages of data by specifying a page number of '2' or higher.
            This argument is not needed if the dataframe data_format is
            requested becuase the function will request all pages of
            data and combine them into one dataframe. Optional.
        mod_since: A string containing an HTTP formatted date and time.
            Causes function to return None if no changes have been
            made to the requested data since the date and time provided.
            Optional.
        only_mod_since: A string containing an HTTP formatted date and
            time. Causes function to only return data that has
            changed since the date and time provided. Optional.

    Returns:
        If session.data_format == "json" or "xml", returns a Python
        dictionary object containing the response text and additional
        metadata. If session.data_format == "dataframe", returns an instances
        of fapy.server.Dframe, which is a Pandas dataframe with
        an additional `attr` property that contains a Python dictionary
        with additional metadata.
    """
    # Check for un-allowed combinations of arguments
    if (team is not None and (event is not None or district is not None
                              or state is not None)):
        raise server.ArgumentError("If you specify team, you cannot "
                                   "specify event, district, or state.")

    cmd = "teams"
    team_args = {"teamNumber": team, "eventCode": event,
                 "districtCode": district, "state": state,
                 "page": page}
    response_lst = [_send_request(session, cmd, team_args, mod_since,
                                  only_mod_since)]

    if ((isinstance(response_lst[0], dict)) or (page is not None) or
            (response_lst[0].attr["code"] == 304)):
        return response_lst[0]

    pages = response_lst[0]["pageTotal"][0]
    if pages == 1:
        return response_lst[0]
    else:
        for page_num in range(2, pages + 1):
            team_args["page"] = str(page_num)
            response_lst.append(_send_request(session, cmd, team_args,
                                              mod_since, only_mod_since))
        response_df = pandas.concat(response_lst)
        response_df.index = range(0, response_df.shape[0])
        response_df.attr = response_lst[-1].attr
    return response_df


def get_schedule(session, event,  # pylint: disable=too-many-arguments
                 level="qual", team=None, start=None, end=None, mod_since=None,
                 only_mod_since=None):
    """Rerieves the FRC competition match schedule.

    Args:
        session: An instance of fapy.classes.Session that contains
            a valid username and authorization key.
        event: A string containing the FIRST API event code.
        level: A string. If "qual", function will return the
            schedule for qualiification matches. If "playoff", will
            return schedule for playoff matches. Optional, default is
            "qual".
        team: FRC team number as a string. If listed, function will
            return data only for that team. Optional.
        start: An integer. If specified, function will return
            matches with match number equal to or higher than start.
        end: An integer. If specified, function will return matches
            with match number equal to or lower than end.
        mod_since: A string containing an HTTP formatted date and time.
            Causes function to return None if no changes have been
            made to the requested data since the date and time provided.
            Optional.
        only_mod_since: A string containing an HTTP formatted date and
            time. Causes function to only return data that has
            changed since the date and time provided. Optional.

  Returns:
        If session.data_format == "json" or "xml", returns a Python
        dictionary object containing the response text and additional
        metadata. If session.data_format == "dataframe", returns an instances
        of fapy.server.Dframe, which is a Pandas dataframe with
        an additional `attr` property that contains a Python dictionary
        with additional metadata.

    """

    sched_args = collections.OrderedDict([("/eventCode", event),
                                          ("teamNumber", team),
                                          ("tournamentLevel", level),
                                          ("start", start),
                                          ("end", end)])

    return _send_request(session, "schedule", sched_args, mod_since,
                         only_mod_since)


def get_hybrid(session, event,  # pylint: disable=too-many-arguments
               level="qual", start=None, end=None, mod_since=None,
               only_mod_since=None):
    """Retrieves the FRC competition match schedule for the requested
    event. For matches that have been played, the schedule will
    include match scores.

    Args:
        session: An instance of fapy.classes.Session that contains
            a valid username and authorization key.
        event: A string containing the FIRST API event code.
        level: A string. If "qual", function will return the
            hybrid schedule for qualiification matches. If "playoff",
            will return hybrid schedule for playoff matches. Optional,
            default is "qual".
        start: An integer. If specified, function will return
            matches with match number equal to or higher than start.
        end: An integer. If specified, function will return matches
            with match number equal to or lower than end.
        mod_since: A string containing an HTTP formatted date and time.
            Causes function to return None if no changes have been
            made to the requested data since the date and time provided.
            Optional.
        only_mod_since: A string containing an HTTP formatted date and
            time. Causes function to only return data that has
            changed since the date and time provided. Optional.

  Returns:
        If session.data_format == "json" or "xml", returns a Python
        dictionary object containing the response text and additional
        metadata. If session.data_format == "dataframe", returns an instances
        of fapy.server.Dframe, which is a Pandas dataframe with
        an additional `attr` property that contains a Python dictionary
        with metadata.

    """
    hybrid_args = collections.OrderedDict([("/eventCode", event),
                                           ("/tournamentLevel", level),
                                           ("/hybrid", "hybrid"),
                                           ("start", start),
                                           ("end", end)])

    response = _send_request(session, "schedule", hybrid_args, mod_since,
                             only_mod_since)
    if isinstance(response, dict):
        response["frame_type"] = "hybrid"
    else:
        response.attr["frame_type"] = "hybrid"
    return response


def get_matches(session, event,  # pylint: disable=too-many-arguments
                level="qual", team=None, match=None, start=None, end=None,
                mod_since=None, only_mod_since=None):
    """Retrieves the match results for an FRC event.

    Args:
        session: An instance of fapy.classes.Session that contains
            a valid username and authorization key.
        event: A string containing the FIRST API event code.
        level: A string. If "qual", function will return the
            hybrid schedule for qualiification matches. If "playoff",
            will return hybrid schedule for playoff matches. Optional,
            default is "qual".
        team: FRC team number as a string. If listed, function will
            return data only for that team. Optional.
        match: A string containing a match number. If specified,
            get_matches returns data only for that match.
        start: An integer. If specified, function will return
            matches with match number equal to or higher than start.
        end: An integer. If specified, function will return matches
            with match number equal to or lower than end.
        mod_since: A string containing an HTTP formatted date and time.
            Causes function to return None if no changes have been
            made to the requested data since the date and time provided.
            Optional.
        only_mod_since: A string containing an HTTP formatted date and
            time. Causes function to only return data that has
            changed since the date and time provided. Optional.

  Returns:
        If session.data_format == "json" or "xml", returns a Python
        dictionary object containing the response text and additional
        metadata. If session.data_format == "dataframe", returns an instances
        of fapy.server.Dframe, which is a Pandas dataframe with
        an additional `attr` property that contains a Python dictionary
        with metadata.
    """

    # Check for argument combinations not allowed by FIRST API
    if match is not None or start is not None or end is not None:
        if level is None:
            raise server.ArgumentError("You must specify the level when you "
                                       "specify match, start, or end.")
    if team is not None and match is not None:
        raise server.ArgumentError("You cannot specify both a team and a "
                                   "match number.")
    if (start is not None or end is not None) and match is not None:
        raise server.ArgumentError("You cannot specify start or end if you "
                                   "specify match.")

    result_args = collections.OrderedDict([("/eventCode", event),
                                           ("tournamentLevel", level),
                                           ("teamNumber", team),
                                           ("matchNumber", match),
                                           ("start", start), ("end", end)])
    return _send_request(session, "matches", result_args, mod_since,
                         only_mod_since)


def get_scores(session, event,  # pylint: disable=too-many-arguments
               level="qual", team=None, match=None, start=None,
               end=None, mod_since=None, only_mod_since=None):
    """Retrieves the detailed match scores for an FRC competition.

    Args:
        session: An instance of fapy.classes.Session that contains
            a valid username and authorization key.
        event: A string containing the FIRST API event code.
        level: A string. If "qual", function will return the
            hybrid schedule for qualiification matches. If "playoff",
            will return hybrid schedule for playoff matches. Optional,
            default is "qual".
        team: FRC team number as a string. If listed, function will
            return data only for that team. Optional.
        match: A string containing a match number. If specified,
            get_matches returns data only for that match.
        start: An integer. If specified, function will return
            matches with match number equal to or higher than start.
        end: An integer. If specified, function will return matches
            with match number equal to or lower than end.
        mod_since: A string containing an HTTP formatted date and time.
            Causes function to return None if no changes have been
            made to the requested data since the date and time provided.
            Optional.
        only_mod_since: A string containing an HTTP formatted date and
            time. Causes function to only return data that has
            changed since the date and time provided. Optional.

  Returns:
        If session.data_format == "json" or "xml", returns a Python
        dictionary object containing the response text and additional
        metadata. If session.data_format == "dataframe", returns an instances
        of fapy.server.Dframe, which is a Pandas dataframe with
        an additional `attr` property that contains a Python dictionary
        with metadata.
    """
    # Check for argument combinations not allowed by FIRST API
    if team is not None and match is not None:
        raise server.ArgumentError("You cannot specify both a team and a "
                                   "match number.")
    if (start is not None or end is not None) and match is not None:
        raise server.ArgumentError("You cannot specify start or end if "
                                   "you specify match.")

    score_args = collections.OrderedDict([("/eventCode", event),
                                          ("/tournamentLevel", level),
                                          ("teamNumber", team),
                                          ("matchNumber", match),
                                          ("start", start),
                                          ("end", end)])

    return _send_request(session, "scores", score_args, mod_since,
                         only_mod_since)


def get_alliances(session, event, mod_since=None, only_mod_since=None):
    """Retrieves the playoff alliances for an FRC competition.

    Args:
        session: An instance of fapy.classes.Session that contains
            a valid username and authorization key.
        event: A string containing the FIRST API event code.
        mod_since: A string containing an HTTP formatted date and time.
            Causes function to return None if no changes have been
            made to the requested data since the date and time provided.
            Optional.
        only_mod_since: A string containing an HTTP formatted date and
            time. Causes function to only return data that has
            changed since the date and time provided. Optional.

        If session.data_format == "json" or "xml", returns a Python
        dictionary object containing the response text and additional
        metadata. If session.data_format == "dataframe", returns an instances
        of fapy.server.Dframe, which is a Pandas dataframe with
        an additional `attr` property that contains a Python dictionary
        with metadata.
    """
    alliance_args = collections.OrderedDict([("/eventCode", event)])

    return _send_request(session, "alliances", alliance_args, mod_since,
                         only_mod_since)


def get_rankings(session, event, team=None, top=None, mod_since=None,
                 only_mod_since=None):
    """Retrieves the team rankings based on the qualification rounds.

    Args:
        session: An instance of fapy.classes.Session that contains
            a valid username and authorization key.
        event: A string containing the FIRST API event code.
        team: FRC team number as a string. If listed, function will
            return data only for that team. Optional.
        top: The number of top-ranked teams to return in the result.
            Optional. Default is to return all teams at the event.
        mod_since: A string containing an HTTP formatted date and time.
            Causes function to return None if no changes have been
            made to the requested data since the date and time provided.
            Optional.
        only_mod_since: A string containing an HTTP formatted date and
            time. Causes function to only return data that has
            changed since the date and time provided. Optional.

    Returns:

    """
    if team is not None and top is not None:
        raise server.ArgumentError("You cannot specifiy both the team "
                                   "and top arguments.")

    rank_args = collections.OrderedDict([("/eventCode", event),
                                         ("teamNumber", team),
                                         ("top", top)])
    return _send_request(session, "rankings", rank_args, mod_since,
                         only_mod_since)


# noinspection PyAttributeOutsideInit
class Session:
    """Contains information required for every FIRST API HTTP request.

    Every fapy method that retrieves data from the FIRST API server
    requires a Session object as the first parameter. The Session
    object contains the FIRST API username, authorization key, and
    competition season, as well as specifies the format of the returned
    data and whether the HTTP request should be sent to the production
    or staging FIRST API servers.
    """
    # pylint: disable=too-many-instance-attributes

    STAGING_URL = "https://frc-staging-api.firstinspires.org"
    PRODUCTION_URL = "https://frc-api.firstinspires.org"
    FIRST_API_VERSION = "v2.0"
    PACKAGE_VERSION = "0.9999"
    USER_AGENT_NAME = "fapy: Version" + PACKAGE_VERSION

    def __init__(self,  # pylint: disable=too-many-arguments
                 username, key, season=None,
                 data_format="dataframe", source="production"):
        """Creates a ``Session`` object.

        *Arguments*
            ``username`` (String)
                The FIRST API account username
            ``key`` (String)
                The FIRST API authorization key
            ``season`` (Integer)
                A four digit year identifying the competition season
                for which data will be retrieved. Optional, defaults
                to the current calendar year.
            ``data_format`` (String)
                Specifies the format of the data that will be returned
                by firstApiPY that submit HTTP requests. The allowed
                values are *dataframe* (Pandas dataframe), *json*, and
                *xml*. Optional, defaults to *dataframe*.
            ``staging`` (Boolean)
                If ``True``, fapy will submit the HTTP request to
                the FIRST API staging server instead of the production
                servers. This option should be used for system testing.
                Optional, defaults to ``False``.
        """

        self.username = username
        self.key = key
        self.season = season
        self.data_format = data_format
        self.source = source

    @property
    def username(self):
        """The account username that is assigned by FIRST API.

        *Type:* String

        """
        return self._username

    @username.setter
    def username(self, username):
        if not isinstance(username, str):
            raise TypeError("username must be a string.")
        else:
            self._username = username  # pylint: disable=W0201
            # pylint W0201: attribute-defined-outside-init

    @property
    def key(self):
        """The account authorization key that is assigned by FIRST API.

        *Type:* String

        """
        return self._key

    @key.setter
    def key(self, key):
        if not isinstance(key, str):
            raise TypeError("key must be a string.")
        else:
            self._key = key  # pylint: disable=W0201
            # pylint W0201: attribute-defined-outside-init

    @property
    def season(self):
        """ FRC competition season.

        Returns: Four-digit integer
        """
        return self._season

    @season.setter
    def season(self, season):
        """A four digit year identifying the competition season_summary.

        Args:
            season: A four digit year. Can be either an integer, a
                string, or None. If None, assigns the current year.

        Raises:
            ValueError if season_summary is prior to 2015 or later than
            current year + 1
        """
        if isinstance(season, str) and season.isnumeric():
            season = int(season)

        current_year = int(datetime.date.today().strftime("%Y"))
        if season is None:
            self._season = current_year  # pylint: disable=W0201
            # pylint W0201: attribute-defined-outside-init
        elif (season >= 2015) and (season <= current_year + 1):
            self._season = season  # pylint: disable=W0201
            # pylint W0201: attribute-defined-outside-init
        else:
            raise ValueError("season_summary must be >= 2015"
                             "and less than current year + 1.")

    @property
    def data_format(self):
        """String specifying format of output from fapy functions.

        *Type:* String

        *Raises:*
            * ``TypeError`` if set to type other than String.
            * ``ValueError`` if other than *dataframe*, *json*, or
              *xml*.
        """
        return self._data_format

    @data_format.setter
    def data_format(self, data_format):

        error_msg = ("The data_format property must be a string containing "
                     "'dataframe', 'json', or 'xml' "
                     "(case insensitive).")
        if not isinstance(data_format, str):
            raise TypeError(error_msg)
        elif data_format.lower() not in ["dataframe", "json", "xml"]:
            raise ValueError(error_msg)
        else:
            self._data_format = data_format.lower()  # pylint: disable=W0201
            # pylint W0201: attribute-defined-outside-init

    @property
    def source(self):
        """Specifies source of FRC data.

        If "production", data comes from FIRST production server. If
        "staging", data comes from FIRST staging server, which is used
        for testing. Data from staging server may not be complete or
        correct. If "local", no http request is made and data comes
        from locally cached files. Local data will match the
        frame_type that was requested (e.g., season, teams, etc.) but
        will not match all requested parameters. Local data is
        intended to be used for testing.

        Returns: A string, either "production", "staging", or "local".
        """
        return self._source

    @source.setter
    def source(self, source):
        if source.lower() in ["production", "staging", "local"]:
            self._source = source  # pylint: disable=W0201
            # pylint W0201: attribute-defined-outside-init
        else:
            self._source = "production"  # pylint: disable=W0201
            # pylint W0201: attribute-defined-outside-init
            warnings.warn("The source argument is not "
                          "recognized. Value should be 'production', "
                          "'staging', or 'local'. Session.source has"
                          "been set to 'production'.", UserWarning)
