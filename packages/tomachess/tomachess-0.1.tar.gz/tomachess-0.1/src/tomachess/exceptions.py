class NotFoundError(Exception):
    pass


class PairingError(ValueError):
    pass


class ResultError(ValueError):
    pass


class TournamentPermissionError(PermissionError):
    pass
