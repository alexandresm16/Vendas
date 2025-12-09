from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.urls import reverse, path
from .forms import ItemVendaInlineForm
from .models import Produto, Estoque, Venda, ItemVenda
from import_export.admin import ExportMixin
from .resources import VendaResource, ItemVendaResource, EstoqueResource


# ================================
# CONFIGURAÇÃO BÁSICA DO ADMIN
# ================================

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
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Produto)
class ProdutoAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ['nome', 'codigo_barras', 'preco']
    search_fields = ['nome', 'codigo_barras']


@admin.register(Estoque)
class EstoqueAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = EstoqueResource
    list_display = ['produto', 'quantidade']
    search_fields = ['produto__nome', 'produto__codigo_barras']


# ================================
# INLINE DE ITENS DA VENDA
# ================================

class ItemVendaInline(admin.TabularInline):
    model = ItemVenda
    form = ItemVendaInlineForm
    extra = 1
    readonly_fields = ['preco_unitario']


# ================================
# ADMIN DE VENDA
# ================================

@admin.register(Venda)
class VendaAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = VendaResource
    inlines = [ItemVendaInline]
    readonly_fields = ['data', 'usuario']
    list_display = ['id', 'data', 'usuario', 'forma_pagamento', 'valor_total']
    list_filter = ['data', 'usuario', 'forma_pagamento']

    # Impede edição de vendas
    def has_change_permission(self, request, obj=None):
        if obj:
            return False
        return True

    # Adiciona usuário na criação
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.usuario = request.user
        super().save_model(request, obj, form, change)

    # ---------------------------------------------
    # INTERCEPTA ADD_VIEW PARA EVITAR DUPLICAÇÃO
    # ---------------------------------------------
    def add_view(self, request, form_url="", extra_context=None):
        """
        Se o POST NÃO tem _confirmar_total → é a primeira etapa
        Então NÃO SALVA NADA e redireciona para a tela de confirmação
        """
        if request.method == "POST" and "_confirmar_total" not in request.POST:
            request.session["venda_post"] = request.POST
            return redirect("admin:core_venda_confirmar")

        # Agora sim permite salvar
        return super().add_view(request, form_url, extra_context)

    # ---------------------------------------------
    # TELA DE CONFIRMAÇÃO
    # ---------------------------------------------
    def confirmar_total(self, request):
        post = request.session.get("venda_post")

        if not post:
            return redirect("/admin/core/venda/add/")

        # Calcula total
        total = 0
        for inline in self.inlines:
            inline_instance = inline(self.model, self.admin_site)
            FormSetClass = inline_instance.get_formset(request)
            formset = FormSetClass(post)

            if formset.is_valid():
                for form in formset.forms:
                    if form.cleaned_data and not form.cleaned_data.get("DELETE"):
                        produto = form.cleaned_data.get("produto")
                        quantidade = form.cleaned_data.get("quantidade")
                        if produto and quantidade:
                            total += produto.preco * quantidade

        # Se usuário clicou em CONFIRMAR
        if request.method == "POST" and "confirmar" in request.POST:
            novo_post = post.copy()
            novo_post["_confirmar_total"] = True

            # Injeta POST final
            request.POST = novo_post

            # Agora salva (apenas UMA vez)
            return self.add_view(request, form_url="", extra_context=None)

        # Renderiza tela
        context = {
            **self.admin_site.each_context(request),
            "title": "Confirmar total da venda",
            "total": total,
            "forma_pagamento": post.get("forma_pagamento"),
        }

        return TemplateResponse(request, "admin/confirmar_total_venda.html", context)

    # Adiciona URL de confirmação
    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "confirmar/",
                self.admin_site.admin_view(self.confirmar_total),
                name="core_venda_confirmar"
            )
        ]
        return custom + urls


# ================================
# ADMIN DE ITEMVENDA (LEITURA)
# ================================

@admin.register(ItemVenda)
class ItemVendaAdmin(ExportMixin, admin.ModelAdmin):
    resource_class = ItemVendaResource
    list_display = ['venda', 'produto', 'quantidade', 'preco_unitario']
    search_fields = ['produto__nome', 'venda__id', 'venda__usuario__username']
    readonly_fields = ['venda', 'produto', 'quantidade', 'preco_unitario']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
