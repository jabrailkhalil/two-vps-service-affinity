"""Pure routing decisions; never promotes a database or changes DNS."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Health:
    reachable: bool
    read_only: bool
    in_recovery: bool
    compatible: bool
    replay_lag_seconds: float = 0

def target(method: str, primary: Health, reserve: Health, max_lag: float = 120) -> str:
    if primary.reachable and primary.compatible and not primary.read_only and not primary.in_recovery:
        return 'primary'
    if (method.upper() in {'GET', 'HEAD'} and reserve.reachable and reserve.compatible
            and reserve.read_only and reserve.in_recovery
            and 0 <= reserve.replay_lag_seconds <= max_lag):
        return 'read-only-reserve'
    return 'unavailable'
