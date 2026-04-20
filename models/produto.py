from dataclasses import dataclass


@dataclass
class Produto:
    id: int | None
    oleo: str
    descricao: str
    quantidade: int
    valor_unitario: float

    @property
    def valor_total(self) -> float:
        return self.quantidade * self.valor_unitario
