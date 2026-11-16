from abc import ABC, abstractmethod

from ..core.context import Context


class Pipeline(ABC):
    # Identifiant utilisé en ligne de commande : <zone>.<identifiant logique>.
    name: str
    description: str

    @abstractmethod
    def run(self, context: Context) -> None: ...
