from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.html import format_html
from django.urls import reverse
from .forms import ItemVendaInlineForm
from .models import Produto, Estoque, Venda, ItemVenda
from import_export.admin import ExportMixin, ImportMixin
from .resources import VendaResource, ItemVendaResource, EstoqueResource

# Personaliza o título e cabeçalho da interface do Django Admin
admin.site.site_header = "Gestão de vendas e estoque"
admin.site.site_title = "Gestão de vendas e estoque"
admin.site.index_title = "Bem-vindo à Gestão de vendas e estoque"


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_link', 'action_flag', 'change_message')
    list_filter = ('user', 'content_type', 'action_flag')
    search_fields = ('object_repr', 'change_message')

    def object_link(self, obj):
        if obj.action_flag == 3:  # DELETED
            return obj.object_repr
        ct = obj.content_type
        try:
            url = reverse(f"admin:{ct.app_label}_{ct.model}_change", args=[obj.object_id])
            return format_html('<a href="{}">{}</a>', url, obj.object_repr)
        except:
            return obj.object_repr

    object_link.short_description = 'Objeto'

    def has_add_permission(self, request):
        return False  # Impede adicionar
    
    def has_change_permission(self, request, obj=None):
        return False  # Permite criar nova

    def has_delete_permission(self, request, obj=None):
        return False  # Impede editar


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
