// Tela do Mapa Leads. Fluxo: enviar busca -> consultar o andamento a cada 3s -> mostrar a tabela.
(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  let empresas = [];

  const aviso = (texto, erro = false) => { $("msg").textContent = texto; $("msg").className = erro ? "erro" : ""; };

  // Só cria links para endereços http(s); qualquer outra coisa vira texto simples.
  const link = (url, rotulo) => {
    if (!/^https?:\/\//i.test(url || "")) return document.createTextNode(url || "");
    const a = document.createElement("a");
    a.href = url; a.target = "_blank"; a.rel = "noopener noreferrer"; a.textContent = rotulo || url;
    return a;
  };
  const dominio = (u) => { try { return new URL(u).hostname.replace(/^www\./, ""); } catch { return u; } };

  function desenhar() {
    const f = $("filtro").value.trim().toLowerCase();
    const lista = empresas.filter((e) => !f || Object.values(e).join(" ").toLowerCase().includes(f));
    $("contagem").textContent = `${lista.length} de ${empresas.length} empresas`;
    const corpo = $("linhas");
    corpo.replaceChildren();
    for (const e of lista) {
      const tr = document.createElement("tr");
      const nome = document.createElement("td");
      nome.append(link(e.link_maps, e.nome) );
      if (!e.link_maps) nome.textContent = e.nome;
      const cel = (conteudo) => { const td = document.createElement("td"); td.append(conteudo); return td; };
      tr.append(
        nome, cel(e.categoria || ""), cel(e.telefone || ""),
        cel(link(e.site, dominio(e.site))), cel(e.email || ""),
        cel(e.nota != null ? `${e.nota} (${e.avaliacoes ?? 0})` : ""), cel(e.endereco || "")
      );
      corpo.append(tr);
    }
    $("resultado").hidden = false;
  }

  const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

  async function api(caminho, opcoes) {
    const r = await fetch(caminho, opcoes);
    const j = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(j.detail || `Erro ${r.status}`);
    return j;
  }

  async function buscar(ev) {
    ev.preventDefault();
    $("buscar").disabled = true;
    $("resultado").hidden = true;
    try {
      aviso("Enviando busca…");
      const { id } = await api("/api/buscas", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ termo: $("termo").value.trim(), cidade: $("cidade").value.trim(), profundidade: +$("prof").value }),
      });
      for (let i = 1; ; i++) {
        const b = await api(`/api/buscas/${encodeURIComponent(id)}`);
        if (b.status === "ok") { empresas = b.empresas; desenhar(); aviso(empresas.length ? "Pronto!" : "A busca terminou sem resultados. Tente outro termo ou cidade."); break; }
        if (b.status === "failed") throw new Error("O Google Maps não respondeu a esta busca. Espere alguns minutos e tente de novo.");
        aviso(`Buscando no Google Maps… (${i * 3}s) — isso pode levar alguns minutos.`);
        await esperar(3000);
      }
    } catch (e) {
      aviso(e.message, true);
    } finally {
      $("buscar").disabled = false;
    }
  }

  $("form").addEventListener("submit", buscar);
  $("filtro").addEventListener("input", desenhar);
})();
