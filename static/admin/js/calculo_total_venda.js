(function() {
    function calcularTotal() {
        let total = 0;

        // Para cada linha do inline
        document.querySelectorAll('.dynamic-itemvenda').forEach(function(row) {
            const quantidadeInput = row.querySelector('input[id$="-quantidade"]');
            const precoInput = row.querySelector('input[id$="-preco_unitario"]');

            if (quantidadeInput && precoInput) {
                const qtd = parseFloat(quantidadeInput.value) || 0;
                const preco = parseFloat(precoInput.value.replace(',', '.')) || 0;
                total += qtd * preco;
            }
        });

        // Exibe no elemento
        const totalElem = document.getElementById("venda-total-preview");
        if (totalElem) {
            totalElem.textContent = total.toFixed(2).replace('.', ',');
        }
    }

    // Calcula ao alterar campos
    document.addEventListener("input", calcularTotal);
    document.addEventListener("change", calcularTotal);

    // Calcula ao carregar página
    document.addEventListener("DOMContentLoaded", calcularTotal);
})();
