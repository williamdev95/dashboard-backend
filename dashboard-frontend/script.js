document.addEventListener("DOMContentLoaded", () => {
  carregarDashboard();
  configurarFiltro();
});

// ===============================
// Função para exibir erros
// ===============================
function mostrarErro(mensagem) {
  const barraErro = document.getElementById("barraErro");
  barraErro.textContent = mensagem;
  barraErro.style.display = "block";

  setTimeout(() => {
    barraErro.style.display = "none";
  }, 5000);
}

// ===============================
// Função para formatar datas BR -> ISO (YYYY-MM-DD)
// ===============================
function formatarDataParaISO(dataBR) {
  if (!dataBR) return null;
  const partes = dataBR.split("-"); // input type="date" já retorna "YYYY-MM-DD"
  if (partes.length === 3) {
    return `${partes[0]}-${partes[1]}-${partes[2]}`;
  }
  return dataBR;
}

// ===============================
// Função principal para carregar tudo
// ===============================
function carregarDashboard(inicio = null, fim = null) {
  let url = "http://127.0.0.1:5000/vendas";

  if (inicio && fim) {
    url += `?inicio=${inicio}&fim=${fim}`;
  }

  fetch(url)
    .then((response) => response.json())
    .then((resposta) => {
      if (resposta.status === "sucesso") {
        const dados = resposta.dados;
        atualizarTotais(dados);
        atualizarTabela(dados);
        atualizarGrafico(dados);

        preencherFiltroProdutos(dados);
      } else {
        mostrarErro(resposta.mensagem || "Erro ao carregar vendas");
      }
    })
    .catch((error) => mostrarErro("Erro ao conectar com o servidor: " + error));
  preencherFiltroProdutos(dados);
}

// ===============================
// Atualizar totais
// ===============================
function atualizarTotais(dados) {
  const totalVendas = dados.length;
  const valorTotal = dados.reduce((acc, v) => acc + v.valor, 0);

  document.getElementById("totalVendas").textContent = totalVendas;
  document.getElementById("valorTotal").textContent = `R$ ${valorTotal.toFixed(
    2
  )}`;
}

// ===============================
// Atualizar tabela de vendas
// ===============================
function atualizarTabela(dados) {
  const tabela = document.getElementById("tabelaVendas");
  tabela.innerHTML = "";

  // 🔽 Ordena os dados por data (mais recente primeiro)
  dados.sort((a, b) => new Date(b.data) - new Date(a.data));

  dados.forEach((venda) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${new Date(venda.data).toLocaleDateString("pt-BR")}</td>
      <td>${venda.produto}</td>
      <td>${venda.quantidade}</td>
      <td>R$ ${venda.valor.toFixed(2)}</td>
    `;
    tabela.appendChild(row);
  });
}
// ===============================
// Preencher filtro de produtos
// ===============================
function preencherFiltroProdutos(dados) {
  const select = document.getElementById("filtroProduto");

  // Captura todos os produtos únicos
  const produtosUnicos = [...new Set(dados.map((venda) => venda.produto))];

  // Limpa opções antigas (deixa só "Todos")
  select.innerHTML = `<option value="todos">Todos</option>`;

  // Adiciona cada produto como opção
  produtosUnicos.forEach((produto) => {
    const option = document.createElement("option");
    option.value = produto;
    option.textContent = produto;
    select.appendChild(option);
  });
}

// ===============================
// Atualizar gráfico de barras
// ===============================
let graficoBarras = null;

function atualizarGrafico(dados) {
  const ctx = document.getElementById("graficoBarras").getContext("2d");

  // Agrupar por produto
  const agrupado = {};
  dados.forEach((v) => {
    if (!agrupado[v.produto]) agrupado[v.produto] = 0;
    agrupado[v.produto] += v.valor;
  });

  const labels = Object.keys(agrupado);
  const valores = Object.values(agrupado);

  if (graficoBarras) {
    graficoBarras.destroy();
  }

  graficoBarras = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Vendas por Produto (R$)",
          data: valores,
          backgroundColor: [
            "rgba(255, 99, 132, 0.7)",
            "rgba(54, 162, 235, 0.7)",
            "rgba(255, 206, 86, 0.7)",
            "rgba(75, 192, 192, 0.7)",
            "rgba(153, 102, 255, 0.7)",
            "rgba(255, 159, 64, 0.7)",
            "rgba(99, 255, 132, 0.7)",
            "rgba(132, 99, 255, 0.7)",
          ],
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
      },
    },
  });
}

// ===============================
// Configurar filtro de datas
// ===============================
function configurarFiltro() {
  const btnFiltrar = document.getElementById("btnFiltrar");
  if (!btnFiltrar) return;

  btnFiltrar.addEventListener("click", () => {
    const inicio = formatarDataParaISO(document.getElementById("inicio").value);
    const fim = formatarDataParaISO(document.getElementById("fim").value);

    if (!inicio || !fim) {
      mostrarErro("Selecione as duas datas para filtrar");
      return;
    }

    carregarDashboard(inicio, fim);
  });
}
// Função para aplicar o filtro de período
document.getElementById("formFiltro").addEventListener("submit", function (e) {
  e.preventDefault();

  const inicio = document.getElementById("dataInicio").value;
  const fim = document.getElementById("dataFim").value;

  fetch(`http://127.0.0.1:5000/filtro?inicio=${inicio}&fim=${fim}`)
    .then((response) => response.json())
    .then((resposta) => {
      if (resposta.status === "sucesso") {
        const dados = resposta.dados;
        atualizarTotais(dados);
        atualizarTabela(dados);
        atualizarGrafico(dados);
      } else {
        mostrarErro(resposta.mensagem || "Erro ao aplicar filtro.");
      }
    })
    .catch((error) => mostrarErro("Erro ao conectar com o servidor: " + error));
});
// ===============================
// Filtro por produto
// ===============================
document
  .getElementById("filtroProduto")
  .addEventListener("change", function () {
    const produtoSelecionado = this.value;

    fetch("http://127.0.0.1:5000/vendas")
      .then((response) => response.json())
      .then((resposta) => {
        if (resposta.status === "sucesso") {
          let dados = resposta.dados;

          // Se não for "Todos", filtra pelo produto escolhido
          if (produtoSelecionado !== "todos") {
            dados = dados.filter(
              (venda) => venda.produto === produtoSelecionado
            );
          }

          atualizarTotais(dados);
          atualizarTabela(dados);
          atualizarGrafico(dados);
        } else {
          mostrarErro(
            resposta.mensagem || "Erro ao aplicar filtro de produto."
          );
        }
      })
      .catch((error) =>
        mostrarErro("Erro ao conectar com o servidor: " + error)
      );
  });
