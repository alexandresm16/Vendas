from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from decimal import Decimal


class Produto(models.Model):
    codigo_barras = models.CharField(max_length=20, unique=True)  # Novo campo
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nome}"


class Estoque(models.Model):
    produto = models.OneToOneField(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.produto.nome} - {self.quantidade}"


class Venda(models.Model):
    FORMA_PAGAMENTO_CHOICES = [
        ('PIX', 'PIX'),
        ('DEBITO', 'Débito'),
        ('DINHEIRO', 'Dinheiro'),
        ('CREDITO', 'Crédito'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)  # Novo campo
    data = models.DateTimeField(auto_now_add=True)
    forma_pagamento = models.CharField(
        max_length=8,
        choices=FORMA_PAGAMENTO_CHOICES,
        default='DINHEIRO',
        verbose_name="Forma de Pagamento"
    )

    def __str__(self):
        return f"Venda {self.id} - {self.data.strftime('%d/%m/%Y %H:%M')}"

    @property
    def valor_total(self):
        total = self.itens.aggregate(
            total=models.Sum(models.F('quantidade') * models.F('preco_unitario'),
                             output_field=models.DecimalField())
        )['total']
        return total or 0


class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, blank=True)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"

    def subtotal(self):
        return self.quantidade * self.preco_unitario

    def clean(self):
        super().clean()

        if self.quantidade is None or self.quantidade < 1:
            raise ValidationError({
                'quantidade': "A quantidade não pode ser vazia ou menor que 1."
            })

        # Verifica estoque
        estoque = Estoque.objects.filter(produto=self.produto).first()
        if estoque and self.quantidade > estoque.quantidade:
            raise ValidationError({
                'quantidade': f"Quantidade solicitada ({self.quantidade}) excede o estoque disponível ({estoque.quantidade})."
            })

    def save(self, *args, **kwargs):
        # Sempre atualiza o preço com o valor atual do produto
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco

        self.full_clean()  # Garante que o clean() seja chamado antes de salvar
        super().save(*args, **kwargs)

        # Atualiza o estoque
        estoque = Estoque.objects.get(produto=self.produto)
        estoque.quantidade -= self.quantidade
        estoque.save()
