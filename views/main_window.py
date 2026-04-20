from __future__ import annotations

from tkinter import messagebox

import customtkinter as ctk

from database import DatabaseManager
from views.lista_produtos import ListaProdutos
from views.produto_form import ProdutoForm


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Estoque")
        self.minsize(900, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.db = DatabaseManager()
        self.current_frame = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._criar_sidebar()
        self.show_produtos()

    def _criar_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(sidebar, text="Sistema de Estoque", font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=0, column=0, padx=16, pady=(24, 20)
        )

        ctk.CTkButton(sidebar, text="📦 Produtos", command=self.show_produtos).grid(row=1, column=0, padx=16, pady=8, sticky="ew")
        ctk.CTkButton(sidebar, text="➕ Novo Produto", command=self.show_novo_produto).grid(row=2, column=0, padx=16, pady=8, sticky="ew")
        ctk.CTkButton(sidebar, text="📊 Relatório", command=self.show_relatorio).grid(row=3, column=0, padx=16, pady=8, sticky="ew")

        ctk.CTkLabel(sidebar, text="Tema").grid(row=4, column=0, padx=16, pady=(20, 8), sticky="w")
        tema = ctk.CTkOptionMenu(sidebar, values=["dark", "light"], command=ctk.set_appearance_mode)
        tema.set("dark")
        tema.grid(row=5, column=0, padx=16, pady=8, sticky="sew")

    def _show_frame(self, frame: ctk.CTkFrame) -> None:
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame
        self.current_frame.grid(row=0, column=1, sticky="nsew")

    def show_produtos(self) -> None:
        frame = ListaProdutos(
            self,
            on_buscar=self._buscar_produtos,
            on_editar=self.show_editar_produto,
            on_excluir=self._excluir_produto,
        )
        self._show_frame(frame)
        self._buscar_produtos("")

    def _buscar_produtos(self, filtro: str) -> None:
        if isinstance(self.current_frame, ListaProdutos):
            produtos = self.db.listar_produtos(filtro)
            self.current_frame.preencher(produtos)

    def show_novo_produto(self) -> None:
        frame = ProdutoForm(self, on_salvar=self._salvar_produto, on_cancelar=self.show_produtos)
        self._show_frame(frame)

    def show_editar_produto(self, produto_id: int) -> None:
        produto = self.db.buscar_produto_por_id(produto_id)
        if not produto:
            messagebox.showerror("Erro", "Produto não encontrado.")
            return
        frame = ProdutoForm(self, on_salvar=self._salvar_produto, on_cancelar=self.show_produtos, produto=produto)
        self._show_frame(frame)

    def _salvar_produto(self, produto_id: int | None, dados: dict[str, str]) -> None:
        try:
            if not dados["oleo"]:
                raise ValueError("O campo Óleo é obrigatório.")
            quantidade = int(dados["quantidade"])
            valor_unitario = float(dados["valor_unitario"])
            if quantidade < 0 or valor_unitario < 0:
                raise ValueError("Quantidade e Valor Unitário não podem ser negativos.")

            if produto_id is None:
                self.db.criar_produto(dados["oleo"], dados["descricao"], quantidade, valor_unitario)
                messagebox.showinfo("Sucesso", "Produto cadastrado com sucesso.")
            else:
                self.db.atualizar_produto(produto_id, dados["oleo"], dados["descricao"], quantidade, valor_unitario)
                messagebox.showinfo("Sucesso", "Produto atualizado com sucesso.")

            self.show_produtos()
        except ValueError as exc:
            messagebox.showerror("Erro de validação", str(exc))

    def _excluir_produto(self, produto_id: int) -> None:
        confirmar = messagebox.askyesno("Confirmar exclusão", "Deseja excluir este produto?")
        if not confirmar:
            return
        self.db.excluir_produto(produto_id)
        messagebox.showinfo("Sucesso", "Produto excluído com sucesso.")
        self._buscar_produtos("")

    def show_relatorio(self) -> None:
        resumo = self.db.obter_resumo()
        frame = ctk.CTkFrame(self)
        frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(frame, text="Relatório", font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(16, 24)
        )

        self._card(frame, "Total de itens", f"{resumo['total_itens']}", 1, 0)
        self._card(frame, "Valor total do estoque", f"R$ {resumo['valor_total']:.2f}", 1, 1)

        maior = resumo["item_maior_valor"]
        menor = resumo["item_menor_estoque"]
        maior_texto = "Sem itens"
        if maior:
            maior_texto = f"{maior['oleo']}\nR$ {maior['total']:.2f}"

        menor_texto = "Sem itens"
        if menor:
            menor_texto = f"{menor['oleo']}\nQtd: {menor['quantidade']}"

        self._card(frame, "Item de maior valor", maior_texto, 2, 0)
        self._card(frame, "Item de menor estoque", menor_texto, 2, 1)

        self._show_frame(frame)

    @staticmethod
    def _card(master, titulo: str, valor: str, row: int, column: int) -> None:
        card = ctk.CTkFrame(master)
        card.grid(row=row, column=column, sticky="nsew", padx=16, pady=8)
        ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=16, pady=(16, 4))
        ctk.CTkLabel(card, text=valor, font=ctk.CTkFont(size=20)).pack(anchor="w", padx=16, pady=(4, 16))
