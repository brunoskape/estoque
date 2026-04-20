from __future__ import annotations

import customtkinter as ctk

from models import Produto


class ListaProdutos(ctk.CTkFrame):
    COLUNAS = [
        ("ID", 50),
        ("Óleo", 120),
        ("Descrição", 260),
        ("Quantidade", 90),
        ("Valor Unit.", 110),
        ("Valor Total", 110),
        ("Ações", 150),
    ]

    def __init__(self, master, on_buscar, on_editar, on_excluir):
        super().__init__(master)
        self.on_buscar = on_buscar
        self.on_editar = on_editar
        self.on_excluir = on_excluir

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        topo.grid_columnconfigure(0, weight=1)

        self.entry_busca = ctk.CTkEntry(topo, placeholder_text="Buscar por nome do óleo")
        self.entry_busca.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry_busca.bind("<Return>", lambda _event: self.on_buscar(self.entry_busca.get()))
        ctk.CTkButton(topo, text="Buscar", width=100, command=lambda: self.on_buscar(self.entry_busca.get())).grid(
            row=0, column=1
        )

        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.grid(row=1, column=0, sticky="nsew", padx=16, pady=(8, 16))
        self.scroll.grid_columnconfigure(0, weight=1)

        self._render_header()

    def _render_header(self) -> None:
        header = ctk.CTkFrame(self.scroll, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=4, pady=(0, 8))
        header.grid_columnconfigure(2, weight=1)

        for idx, (texto, largura) in enumerate(self.COLUNAS):
            ctk.CTkLabel(header, text=texto, width=largura, anchor="w", font=ctk.CTkFont(weight="bold")).grid(
                row=0, column=idx, sticky="w", padx=4
            )

    def preencher(self, produtos: list[Produto]) -> None:
        for widget in self.scroll.winfo_children()[1:]:
            widget.destroy()

        for i, produto in enumerate(produtos, start=1):
            row = ctk.CTkFrame(self.scroll)
            row.grid(row=i, column=0, sticky="ew", padx=4, pady=4)
            row.grid_columnconfigure(2, weight=1)

            valores = [
                str(produto.id),
                produto.oleo,
                produto.descricao,
                str(produto.quantidade),
                f"R$ {produto.valor_unitario:.2f}",
                f"R$ {produto.valor_total:.2f}",
            ]

            for idx, (texto, (_, largura)) in enumerate(zip(valores, self.COLUNAS[:6], strict=False)):
                ctk.CTkLabel(row, text=texto, width=largura, anchor="w").grid(row=0, column=idx, sticky="w", padx=4)

            botoes = ctk.CTkFrame(row, fg_color="transparent")
            botoes.grid(row=0, column=6, sticky="e", padx=4)
            ctk.CTkButton(botoes, text="Editar", width=65, command=lambda p=produto: self.on_editar(p.id)).pack(
                side="left", padx=(0, 6)
            )
            ctk.CTkButton(
                botoes,
                text="Excluir",
                width=65,
                fg_color="#b53030",
                hover_color="#902525",
                command=lambda p=produto: self.on_excluir(p.id),
            ).pack(side="left")

        if not produtos:
            ctk.CTkLabel(self.scroll, text="Nenhum produto encontrado.").grid(row=1, column=0, pady=16)
