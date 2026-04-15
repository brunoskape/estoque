from __future__ import annotations

import sqlite3
from pathlib import Path

from models import Produto


class DatabaseManager:
    def __init__(self, db_path: str = "estoque.db") -> None:
        self.db_path = Path(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    oleo TEXT NOT NULL,
                    descricao TEXT,
                    quantidade INTEGER NOT NULL DEFAULT 0,
                    valor_unitario REAL NOT NULL DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )

    @staticmethod
    def _row_to_produto(row: sqlite3.Row) -> Produto:
        return Produto(
            id=row["id"],
            oleo=row["oleo"],
            descricao=row["descricao"] or "",
            quantidade=row["quantidade"],
            valor_unitario=row["valor_unitario"],
        )

    def listar_produtos(self, filtro: str = "") -> list[Produto]:
        query = "SELECT * FROM produtos"
        params: tuple[str, ...] = ()
        if filtro.strip():
            query += " WHERE oleo LIKE ?"
            params = (f"%{filtro.strip()}%",)
        query += " ORDER BY oleo COLLATE NOCASE"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_produto(row) for row in rows]

    def buscar_produto_por_id(self, produto_id: int) -> Produto | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
        return self._row_to_produto(row) if row else None

    def criar_produto(self, oleo: str, descricao: str, quantidade: int, valor_unitario: float) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO produtos (oleo, descricao, quantidade, valor_unitario)
                VALUES (?, ?, ?, ?)
                """,
                (oleo.strip(), descricao.strip(), quantidade, valor_unitario),
            )

    def atualizar_produto(self, produto_id: int, oleo: str, descricao: str, quantidade: int, valor_unitario: float) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE produtos
                SET oleo = ?, descricao = ?, quantidade = ?, valor_unitario = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (oleo.strip(), descricao.strip(), quantidade, valor_unitario, produto_id),
            )

    def excluir_produto(self, produto_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))

    def obter_resumo(self) -> dict[str, object]:
        with self._connect() as conn:
            total_itens = conn.execute("SELECT COALESCE(SUM(quantidade), 0) AS total FROM produtos").fetchone()["total"]
            valor_total = conn.execute(
                "SELECT COALESCE(SUM(quantidade * valor_unitario), 0) AS total FROM produtos"
            ).fetchone()["total"]

            maior_valor_row = conn.execute(
                """
                SELECT oleo, quantidade, valor_unitario, (quantidade * valor_unitario) AS total
                FROM produtos
                ORDER BY total DESC, id ASC
                LIMIT 1
                """
            ).fetchone()
            menor_estoque_row = conn.execute(
                """
                SELECT oleo, quantidade
                FROM produtos
                ORDER BY quantidade ASC, id ASC
                LIMIT 1
                """
            ).fetchone()

        return {
            "total_itens": int(total_itens),
            "valor_total": float(valor_total),
            "item_maior_valor": dict(maior_valor_row) if maior_valor_row else None,
            "item_menor_estoque": dict(menor_estoque_row) if menor_estoque_row else None,
        }
