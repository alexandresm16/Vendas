from django.utils.timezone import now
from django.views.generic import TemplateView
from .models import Venda, ItemVenda
from django.db.models import Sum, ExpressionWrapper, F, DecimalField, Count
from django.shortcuts import redirect, render


def home(request):
    return render(request, 'home.html')


class DashboardVendasView(TemplateView):
    template_name = 'dashboard_vendas.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Total geral vendido
        total_geral = Venda.objects.annotate(
            total_venda=Sum(
                ExpressionWrapper(
                    F('itens__quantidade') * F('itens__preco_unitario'),
                    output_field=DecimalField()
                )
            )
        ).aggregate(total=Sum('total_venda'))['total'] or 0

        # Total vendido no mês atual
        hoje = now()
        total_mes = Venda.objects.filter(
            data__year=hoje.year,
            data__month=hoje.month
        ).annotate(
            total_venda=Sum(
                ExpressionWrapper(
                    F('itens__quantidade') * F('itens__preco_unitario'),
                    output_field=DecimalField()
                )
            )
        ).aggregate(total=Sum('total_venda'))['total'] or 0

        # Quantidade total de itens vendidos
        total_itens_geral = ItemVenda.objects.aggregate(total=Sum('quantidade'))['total'] or 0

        # Quantidade de itens vendidos no mês atual
        total_itens_mes = ItemVenda.objects.filter(
            venda__data__year=hoje.year,
            venda__data__month=hoje.month
        ).aggregate(total=Sum('quantidade'))['total'] or 0

        inicio_mes = hoje.replace(day=1)

        # Contagem total por forma de pagamento
        formas_geral = Venda.objects.values('forma_pagamento').annotate(total=Count('id'))

        # Contagem mensal por forma de pagamento
        formas_mes = Venda.objects.filter(data__gte=inicio_mes).values('forma_pagamento').annotate(total=Count('id'))

        context['formas_geral'] = list(formas_geral)
        context['formas_mes'] = list(formas_mes)

        # Adiciona ao contexto do template
        context.update({
            'total_geral': total_geral,
            'total_mes': total_mes,
            'total_itens_geral': total_itens_geral,
            'total_itens_mes': total_itens_mes,
        })

        return context
