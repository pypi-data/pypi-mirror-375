from typing import TYPE_CHECKING, Annotated, Union

from pydantic import Field

from tomachess.base import (
    AbstractParameters,
    AbstractStates,
    TeamTournamentBase,
    TournamentBase
)
from tomachess.registry import ParametersRegistry, StatesRegistry, TeamTournamentRegistry, TournamentRegistry

if TYPE_CHECKING:
    Parameters = Annotated[Union[AbstractParameters], Field(discriminator="type")]
    States = Annotated[Union[AbstractStates], Field(discriminator="type")]
    Tournament = Annotated[Union[TournamentBase], Field(discriminator="type")]
    TeamTournament = Annotated[Union[TeamTournamentBase], Field(discriminator="type")]
else:
    parameters_values_tuple = tuple(ParametersRegistry.get_all())
    states_values_tuple = tuple(StatesRegistry.get_all())
    tournaments_values_tuple = tuple(TournamentRegistry.get_all().values())
    team_tournaments_values_tuple = tuple(TeamTournamentRegistry.get_all().values())

    Parameters = Annotated[Union[parameters_values_tuple], Field(discriminator="type")]
    States = Annotated[Union[states_values_tuple], Field(discriminator="type")]
    Tournament = Annotated[Union[tournaments_values_tuple], Field(discriminator="type")]
    TeamTournament = Annotated[Union[team_tournaments_values_tuple], Field(discriminator="type")]
