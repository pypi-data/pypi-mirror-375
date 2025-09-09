from tomachess.participant import Player
from tomachess.state.pairings import Pairings
from tomachess.state.results import RoundResult, IndividualResult
from tomachess.tournament.round_robin import RoundRobinTournament
from tomachess.union_type import Tournament

players = [Player(name=str(i)) for i in range(2)]
r = RoundRobinTournament(participants=players)
r.parameters.cycles = 2
r.generate_pairings()
pairings = r.get_pairings()
assert pairings is not None and Pairings.is_finalized(pairings)
round_result = RoundResult.from_pairings(pairings)
round_result.items[0].result_1 = IndividualResult.WIN
round_result.items[0].result_2 = IndividualResult.LOSS
r.add_round_result(round_result)
r.generate_pairings()
pairings = r.get_pairings()
assert pairings is not None and Pairings.is_finalized(pairings)
round_result = RoundResult.from_pairings(pairings)
round_result.items[0].result_1 = IndividualResult.LOSS
round_result.items[0].result_2 = IndividualResult.WIN
r.add_round_result(round_result)
print("Standings")
print(r.get_standings())

dumps = r.model_dump_json()
print("Tournament (JSON)")
print(dumps)
s = Tournament.model_validate_json(dumps)
print("Tournament")
print(s)
