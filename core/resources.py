from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Venda, ItemVenda, Estoque
from django.contrib.auth.models import User


class VendaResource(resources.ModelResource):
    usuario = fields.Field(
        column_name='usuario',
        attribute='usuario',
        widget=ForeignKeyWidget(User, 'username')  # ou 'get_full_name'
    )

    valor_total = fields.Field(column_name='valor_total')
    itens = fields.Field(column_name='itens')
    quantidade_total_itens = fields.Field(column_name='quantidade_total_itens')  # <-- novo campo

    def dehydrate_valor_total(self, obj):
        return f"{obj.valor_total:.2f}".replace('.', ',')

    def dehydrate_itens(self, obj):
        itens_formatados = []
        for item in obj.itens.all():
            itens_formatados.append(
                f"{item.produto.nome} (Qtd: {item.quantidade}, Valor Unitario: {item.preco_unitario})"
            )
        return " - ".join(itens_formatados)

    def dehydrate_quantidade_total_itens(self, obj):
        return sum(item.quantidade for item in obj.itens.all())

    class Meta:
        model = Venda
        fields = ('id', 'data', 'usuario', 'forma_pagamento', 'quantidade_total_itens', 'itens', 'valor_total')
        export_order = ('id', 'data', 'usuario', 'forma_pagamento', 'quantidade_total_itens', 'itens', 'valor_total')


class ItemVendaResource(resources.ModelResource):
    venda_id = fields.Field(column_name='id_venda', attribute='venda', widget=ForeignKeyWidget(Venda, 'id'))
    data_venda = fields.Field(column_name='data_venda')
    usuario = fields.Field(column_name='usuario')
    produto = fields.Field(column_name='produto')
    forma_pagamento = fields.Field(column_name='forma_pagamento')
    subtotal = fields.Field(column_name='subtotal')

    def dehydrate_subtotal(self, obj):
        return f"{obj.quantidade * obj.preco_unitario:.2f}".replace('.', ',')

    def dehydrate_data_venda(self, obj):
        return obj.venda.data.strftime('%Y-%m-%d %H:%M')

    def dehydrate_usuario(self, obj):
        return obj.venda.usuario.username

    def dehydrate_produto(self, obj):
        return obj.produto.nome

    def dehydrate_subtotal(self, obj):
        return obj.quantidade * obj.preco_unitario

    def dehydrate_forma_pagamento(self, obj):
        return obj.venda.get_forma_pagamento_display()

    class Meta:
        model = ItemVenda
        fields = ('venda_id', 'data_venda', 'usuario', 'produto', 'quantidade', 'preco_unitario', 'subtotal',
                  'forma_pagamento')
        export_order = ('venda_id', 'data_venda', 'usuario', 'produto', 'quantidade', 'preco_unitario', 'subtotal',
                        'forma_pagamento')


class EstoqueResource(resources.ModelResource):
    produto = fields.Field(column_name='produto')
    codigo_barras = fields.Field(column_name='codigo_barras')

    def dehydrate_produto(self, obj):
        return obj.produto.nome

    def dehydrate_codigo_barras(self, obj):
        return obj.produto.codigo_barras

    class Meta:
        model = Estoque
        fields = ('produto', 'codigo_barras', 'quantidade')
        export_order = ('produto', 'codigo_barras', 'quantidade')
