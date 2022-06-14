# xG Client

PHP client for [football (soccer) expected goals (xG) statistics API](https://rapidapi.com/Wolf1984/api/football-xg-statistics/).
It provides a list of events with xG metric for every game of more than 80 leagues.

## Usage

To install the latest version of `xgclient` use [pip](https://pypi.org/project/pip/).

```bash
pip install xgclient
```

## Example usage

Basic Usage
```python
from xgclient.client import ExpectedGoalsClient

client = ExpectedGoalsClient('Your API Key')

countries = client.countries() # list of countries
tournaments = client.tournaments(country_id) # list of leagues for specified country
seasons = client.seasons(league_id) # list of seasons for specified league
fixtures = client.fixtures(season_id) # list of fixtures for specified season
fixture = client.fixture(fixture_id) # get one fixture
```

Calculating xg90 (expected goals for 90 minutes) metric for every team of available seasons 
```python
import operator
from xgclient.client import ExpectedGoalsClient

client = ExpectedGoalsClient('Your API key')

for country in client.countries():
    for tournament in client.tournaments(country['id']):
        for season in client.seasons(tournament['id']):
            print(country['name'], tournament['name'], season['name'])
            print('=====')

            season_fixtures = client.fixtures(season['id'])

            expected_goals = {}
            minutes = {}
            team_names = {}
            for fixture in season_fixtures:
                if not team_names.get(fixture['homeTeam']['id']):
                    team_names[fixture['homeTeam']['id']] = fixture['homeTeam']['name']
                    minutes[fixture['homeTeam']['id']] = 0

                if not team_names.get(fixture['awayTeam']['id']):
                    team_names[fixture['awayTeam']['id']] = fixture['awayTeam']['name']
                    minutes[fixture['awayTeam']['id']] = 0

                fixture_duration = fixture['duration']['firstHalf'] + fixture['duration']['secondHalf']

                minutes[fixture['homeTeam']['id']] += fixture_duration
                minutes[fixture['awayTeam']['id']] += fixture_duration

                for event in fixture['events']:
                    if not event['xg']:
                        continue

                    if not expected_goals.get(event['teamId']):
                        expected_goals[event['teamId']] = 0

                    expected_goals[event['teamId']] += event['xg']

            result = {}
            for team_id in expected_goals:
                result[team_id] = (expected_goals[team_id] / minutes[team_id]) * 90

            result = sorted(result.items(), key=operator.itemgetter(1), reverse=True)

            for team_id, value in result:
                print(team_names[team_id], value)

            print('')
```

Example Output:
```
England Premier League 2016/2017
=====
Manchester City 2.2112692731277535
Tottenham 2.052839403973515
Chelsea 1.826269731376351
Arsenal 1.799702725020647
Liverpool 1.69972352778546
Manchester Utd 1.6932413793103451
Southampton 1.439378453038676
Everton 1.3932328539823016
Bournemouth 1.2910729023383791
Stoke 1.2596034150371813
Leicester 1.212548156301597
West Ham 1.2049150684931513
Crystal Palace 1.1981870860927168
Swansea 1.0498671831765367
Burnley 0.9535088202866603
Watford 0.9309592061742009
West Brom 0.9158252695604089
Sunderland 0.9000000000000007
Hull 0.8362012717721877
Middlesbrough 0.6971943443304693

England Premier League 2017/2018
=====
Manchester City 2.398823204419891
Liverpool 1.871100993377485
Tottenham 1.8331631244824735
Arsenal 1.6883651452282165
Manchester Utd 1.5726460005535572
Chelsea 1.4510011061946915
Crystal Palace 1.403015741507872
Leicester 1.2518565517241396
Watford 1.1562657534246574
Everton 1.1204689655172415
Newcastle 1.0640897755610998
West Ham 1.0446826051112954
Bournemouth 0.9957362637362651
Brighton 0.9839266870313802
Southampton 0.9228472987872113
Stoke 0.8937382661512978
Burnley 0.8835910224438907
West Brom 0.8344257316399778
Swansea 0.7753942254303168
Huddersfield 0.7536753318584073

```

