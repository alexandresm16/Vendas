from django.contrib import admin

from .forms import ItemVendaInlineForm
from .models import Produto, Estoque, Venda, ItemVenda
from import_export.admin import ExportMixin, ImportMixin

from .resources import VendaResource, ItemVendaResource, EstoqueResource


@admin.register(Produto)
class ProdutoAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ['nome', 'codigo_barras', 'preco']
    search_fields = ['nome', 'codigo_barras']


@admin.register(Estoque)
class EstoqueAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = EstoqueResource
    list_display = ['produto', 'quantidade']
    search_fields = ['produto__nome', 'produto__codigo_barras']


class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    form = ItemVendaInlineForm  # <- Usando o form com o label personalizado
    extra = 1
    readonly_fields = ['preco_unitario']


@admin.register(Venda)
class VendaAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = VendaResource  # <-- Aqui está a mágica
    inlines = [ItemVendaInline]
    readonly_fields = ['data', 'usuario']
    list_display = ['id', 'data', 'usuario', 'forma_pagamento', 'valor_total']
    list_filter = ['data', 'usuario', 'forma_pagamento']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user  # Atribui o usuário logado ao criar a venda
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        if obj:  # Se a venda já existe
            return False  # Impede editar completamente
        return True  # Permite criar nova


@admin.register(ItemVenda)
class ItemVendaAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ItemVendaResource
    list_display = ['venda', 'produto', 'quantidade', 'preco_unitario']
    search_fields = ['produto__nome', 'venda__id', 'venda__usuario__username']
    readonly_fields = ['venda', 'produto', 'quantidade', 'preco_unitario']  # Só leitura no detalhe

    def has_add_permission(self, request):
        return False  # Impede adicionar

    def has_change_permission(self, request, obj=None):
        return False  # Impede editar
