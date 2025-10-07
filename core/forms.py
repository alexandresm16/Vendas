from django import forms
from .models import ItemVenda, Produto, Estoque

class ItemVendaInlineForm(forms.ModelForm):
    class Meta:
        model = ItemVenda
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Obtém IDs dos produtos com estoque > 0
        produtos_com_estoque = Estoque.objects.filter(quantidade__gt=0).values_list('produto_id', flat=True)

        # Filtra o queryset do campo produto
        self.fields['produto'].queryset = Produto.objects.filter(id__in=produtos_com_estoque)
