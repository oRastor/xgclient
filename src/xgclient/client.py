from marshmallow import Schema, fields
import requests


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
    odds = fields.Nested(EventSchema, many=True, default=[])


class ExpectedGoalsClient:
    def __init__(self, key: str, base_url: str = 'https://football-xg-statistics.p.rapidapi.com'):
        self.base_url = base_url
        self.headers = {
            'X-RapidAPI-Key': key,
            'X-RapidAPI-Host': 'football-xg-statistics.p.rapidapi.com',
            'User-Agent': 'xgclient-0.1'
        }

    def countries(self):
        json = self.request(str.join('', [self.base_url, '/countries/']))

        return CountrySchema().dump(json['result'], many=True)

    def tournaments(self, country_id: int):
        json = self.request(str.join('', [self.base_url, '/countries/', str(country_id), '/leagues/']))

        return TournamentSchema().dump(json['result'], many=True)

    def seasons(self, tournament_id: int):
        json = self.request(str.join('', [self.base_url, '/leagues/', str(tournament_id), '/seasons/']))

        return SeasonSchema().dump(json['result'], many=True)

    def fixtures(self, season_id: int):
        json = self.request(str.join('', [self.base_url, '/seasons/', str(season_id), '/fixtures/']))

        return FixtureSchema().dump(json['result'], many=True)

    def fixture(self, fixture_id: int):
        json = self.request(str.join('', [self.base_url, '/fixtures/', str(fixture_id), '/']))

        return FixtureSchema().dump(json['result'])

    def request(self, url):
        response = requests.request("GET", url, headers=self.headers)
        response.raise_for_status()

        return response.json()
