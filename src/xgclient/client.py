from enum import Enum

from marshmallow import Schema, fields
import requests
from datetime import datetime
from pandas import DataFrame


class CountrySchema(Schema):
    id = fields.Int()
    name = fields.Str()


class TournamentSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class SeasonSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class TeamSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class DurationSchema(Schema):
    total = fields.Int()
    firstHalf = fields.Int()
    secondHalf = fields.Int()


class ScoreSchema(Schema):
    final = fields.Int()
    firstHalf = fields.Int()


class AuthorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class EventSchema(Schema):
    homeScore = fields.Int()
    awayScore = fields.Int()
    minute = fields.Int()
    additionalMinute = fields.Int(default=None)
    author = fields.Nested(AuthorSchema)
    teamId = fields.Int()
    type = fields.Str()
    xg = fields.Float()


class OddsSchema(Schema):
    type = fields.Str()
    open = fields.Float()
    last = fields.Float()


class FixtureSchema(Schema):
    id = fields.Int()
    status = fields.Str()
    startTime = fields.Int()
    updateTime = fields.Int()
    homeTeam = fields.Nested(TeamSchema)
    awayTeam = fields.Nested(TeamSchema)
    duration = fields.Nested(DurationSchema)
    homeScore = fields.Nested(ScoreSchema)
    awayScore = fields.Nested(ScoreSchema)
    country = fields.Nested(CountrySchema)
    tournament = fields.Nested(TournamentSchema)
    season = fields.Nested(SeasonSchema)
    events = fields.Nested(EventSchema, many=True, default=[])
    odds = fields.Nested(OddsSchema, many=True, default=[])


class FixtureOddsSchema(Schema):
    gameId = fields.Int()
    odds = fields.Nested(OddsSchema, many=True, default=[])


class Type(Enum):
    RAPID = 1,
    DIRECT = 2


class ExpectedGoalsClient:
    def __init__(self, key: str, api_type: Type = Type.RAPID):
        self.type = api_type
        self.key = key
        if api_type == Type.RAPID:
            self.base_url = 'https://football-xg-statistics.p.rapidapi.com'
            self.headers = {
                'X-RapidAPI-Key': key,
                'X-RapidAPI-Host': 'football-xg-statistics.p.rapidapi.com',
                'User-Agent': 'xgclient-0.1'
            }
        elif api_type == Type.DIRECT:
            self.base_url = 'https://offvariance.com/api/v2/json'
            self.headers = {
                'User-Agent': 'xgclient-0.1'
            }

    def countries(self):
        json = self.request(str.join('', [self.base_url, '/countries/']))

        return CountrySchema().dump(json['result'], many=True)

    def tournaments(self, country_id: int):
        json = self.request(str.join('', [self.base_url, '/countries/', str(country_id), '/tournaments/']))

        return TournamentSchema().dump(json['result'], many=True)

    def seasons(self, tournament_id: int):
        json = self.request(str.join('', [self.base_url, '/tournaments/', str(tournament_id), '/seasons/']))

        return SeasonSchema().dump(json['result'], many=True)

    def fixtures(self, season_id: int):
        json = self.request(str.join('', [self.base_url, '/seasons/', str(season_id), '/fixtures/']))

        return FixtureSchema().dump(json['result'], many=True)

    def fixture(self, fixture_id: int):
        json = self.request(str.join('', [self.base_url, '/fixtures/', str(fixture_id), '/']))

        return FixtureSchema().dump(json['result'])

    def upcoming_odds(self):
        json = self.request(str.join('', [self.base_url, '/odds/upcoming/']))

        return FixtureOddsSchema().dump(json['result'], many=True)

    def request(self, url):
        if self.type == Type.RAPID:
            response = requests.request("GET", url, params={'key': self.key}, headers=self.headers)
            response.raise_for_status()

            return response.json()

        response = requests.request("GET", url, headers=self.headers)
        response.raise_for_status()

        return response.json()


def prepare_odds_type(type):
    if type == 'totalUnder25':
        return 'total_under_2_5'

    if type == 'totalOver25':
        return 'total_over_2_5'

    return type


def create_fixture_odds(items):
    result = []
    for item in items:
        fixture_dict = {
            'id': item['gameId'],
        }

        for oddsItem in item['odds']:
            odds_type = prepare_odds_type(oddsItem['type'])

            fixture_dict['odds_' + odds_type + '_open'] = oddsItem['open']
            fixture_dict['odds_' + odds_type + '_last'] = oddsItem['last']

        result.append(fixture_dict)

    return DataFrame(result)


def create_fixtures_dataframe(fixtures):
    result = []
    for fixture in fixtures:
        if not fixture.get('homeTeam') or not fixture.get('awayTeam'):
            continue

        date = None
        if isinstance(fixture['startTime'], int):
            date = datetime.fromtimestamp(fixture['startTime'])

        fixture_dict = {
            'id': fixture['id'],
            'status': fixture['status'],
            'date': date,
            'start_time': fixture['startTime'],
            'update_time': fixture['updateTime'],
            'country_id': fixture['country']['id'],
            'country_name': fixture['country']['name'],
            'tournament_id': fixture['tournament']['id'],
            'tournament_name': fixture['tournament']['name'],
            'season_id': fixture['season']['id'],
            'season_name': fixture['season']['name'],
            'home_team_id': fixture['homeTeam']['id'],
            'home_team_name': fixture['homeTeam']['name'],
            'away_team_id': fixture['awayTeam']['id'],
            'away_team_name': fixture['awayTeam']['name'],
        }

        if fixture.get('homeScore'):
            fixture_dict['home_score_final'] = fixture['homeScore']['final']
            fixture_dict['home_score_first_half'] = fixture['homeScore']['firstHalf']

        if fixture.get('awayScore'):
            fixture_dict['away_score_final'] = fixture['awayScore']['final']
            fixture_dict['away_score_first_half'] = fixture['awayScore']['firstHalf']

        if fixture.get('duration'):
            fixture_dict['duration_total'] = fixture['duration']['total']
            fixture_dict['duration_first_half'] = fixture['duration']['firstHalf']
            fixture_dict['duration_second_half'] = fixture['duration']['secondHalf']

        for oddsItem in fixture['odds']:
            odds_type = prepare_odds_type(oddsItem['type'])

            fixture_dict['odds_' + odds_type + '_open'] = oddsItem['open']
            fixture_dict['odds_' + odds_type + '_last'] = oddsItem['last']

        result.append(fixture_dict)

    result_df = DataFrame(result,
                          columns=['id', 'status', 'date', 'start_time', 'update_time', 'country_id', 'country_name',
                                   'tournament_id', 'tournament_name', 'season_id', 'season_name',
                                   'home_team_id',
                                   'home_team_name', 'away_team_id', 'away_team_name', 'home_score_final',
                                   'home_score_first_half', 'away_score_final', 'away_score_first_half',
                                   'duration_total', 'duration_first_half', 'duration_second_half',
                                   'odds_home_open',
                                   'odds_home_last', 'odds_draw_open', 'odds_draw_last', 'odds_away_open',
                                   'odds_away_last', 'odds_total_over_2_5_open', 'odds_total_over_2_5_last',
                                   'odds_total_under_2_5_open', 'odds_total_under_2_5_last'])

    result_df.sort_values(by=['start_time'], inplace=True)

    return result_df


def create_events_dataframe(fixtures):
    result = []
    for fixture in fixtures:
        for event in fixture['events']:
            result.append({
                'game_id': fixture['id'],
                'minute': event['minute'],
                'additional_minute': event['additionalMinute'],
                'team_id': event['teamId'],
                'type': event['type'],
                'home_score': event['homeScore'],
                'away_score': event['awayScore'],
                'author_id': event['author']['id'],
                'author_name': event['author']['name'],
                'xg': event['xg'],
            })

    return DataFrame(result)
