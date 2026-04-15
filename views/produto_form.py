from __future__ import annotations

import customtkinter as ctk

from models import Produto


class ProdutoForm(ctk.CTkFrame):
    def __init__(self, master, on_salvar, on_cancelar, produto: Produto | None = None):
        super().__init__(master)
        self.on_salvar = on_salvar
        self.on_cancelar = on_cancelar
        self.produto = produto

        self.grid_columnconfigure(1, weight=1)

        titulo = "Editar Produto" if produto else "Novo Produto"
        ctk.CTkLabel(self, text=titulo, font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(16, 24)
        )

        ctk.CTkLabel(self, text="Óleo *").grid(row=1, column=0, sticky="w", padx=16, pady=8)
        self.entry_oleo = ctk.CTkEntry(self, placeholder_text="Ex.: 5W30")
        self.entry_oleo.grid(row=1, column=1, sticky="ew", padx=16, pady=8)

        ctk.CTkLabel(self, text="Descrição").grid(row=2, column=0, sticky="w", padx=16, pady=8)
        self.entry_descricao = ctk.CTkEntry(self, placeholder_text="Descrição do produto")
        self.entry_descricao.grid(row=2, column=1, sticky="ew", padx=16, pady=8)

        ctk.CTkLabel(self, text="Quantidade *").grid(row=3, column=0, sticky="w", padx=16, pady=8)
        self.entry_quantidade = ctk.CTkEntry(self, placeholder_text="0")
        self.entry_quantidade.grid(row=3, column=1, sticky="ew", padx=16, pady=8)

        ctk.CTkLabel(self, text="Valor Unitário (R$) *").grid(row=4, column=0, sticky="w", padx=16, pady=8)
        self.entry_valor_unitario = ctk.CTkEntry(self, placeholder_text="0.00")
        self.entry_valor_unitario.grid(row=4, column=1, sticky="ew", padx=16, pady=8)

        botoes = ctk.CTkFrame(self, fg_color="transparent")
        botoes.grid(row=5, column=0, columnspan=2, sticky="e", padx=16, pady=(24, 16))

        ctk.CTkButton(botoes, text="Cancelar", fg_color="gray40", command=self.on_cancelar).pack(side="right", padx=(8, 0))
        ctk.CTkButton(botoes, text="Salvar", command=self._salvar).pack(side="right")

        if produto:
            self.entry_oleo.insert(0, produto.oleo)
            self.entry_descricao.insert(0, produto.descricao)
            self.entry_quantidade.insert(0, str(produto.quantidade))
            self.entry_valor_unitario.insert(0, f"{produto.valor_unitario:.2f}")

    def _salvar(self) -> None:
        dados = {
            "oleo": self.entry_oleo.get().strip(),
            "descricao": self.entry_descricao.get().strip(),
            "quantidade": self.entry_quantidade.get().strip(),
            "valor_unitario": self.entry_valor_unitario.get().strip().replace(",", "."),
        }
        self.on_salvar(self.produto.id if self.produto else None, dados)
