/* Cães Maravilhosos — interações do site (menu, animações, galeria e orçamento) */
(function () {
  "use strict";

  var WHATSAPP = "5511947225465";
  var reduzMovimento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- Cabeçalho: sombra ao rolar ---------- */
  var header = document.querySelector(".site-header");
  if (header) {
    var marcar = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    marcar();
    window.addEventListener("scroll", marcar, { passive: true });
  }

  /* ---------- Menu mobile ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("menu-principal");
  if (toggle && nav) {
    var abrir = function (aberto) {
      toggle.setAttribute("aria-expanded", String(aberto));
      toggle.setAttribute("aria-label", aberto ? "Fechar menu" : "Abrir menu");
      nav.classList.toggle("is-open", aberto);
      document.body.classList.toggle("menu-open", aberto);
      if (aberto) {
        var primeiro = nav.querySelector("a");
        if (primeiro) primeiro.focus();
      }
    };
    toggle.addEventListener("click", function () {
      abrir(toggle.getAttribute("aria-expanded") !== "true");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        abrir(false);
        toggle.focus();
      }
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) abrir(false);
    });
    window.matchMedia("(min-width: 1100px)").addEventListener("change", function (mq) {
      if (mq.matches) abrir(false);
    });
  }

  /* ---------- Animações de entrada ---------- */
  var revelaveis = document.querySelectorAll(".reveal, .reveal-pop");
  if ("IntersectionObserver" in window && !reduzMovimento) {
    var io = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add("is-visible");
          io.unobserve(en.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
    revelaveis.forEach(function (el) { io.observe(el); });
  } else {
    revelaveis.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* ---------- Contadores ---------- */
  var formatar = function (valor, casas) {
    return valor.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
  };
  var contar = function (el) {
    var alvo = parseFloat(el.getAttribute("data-count"));
    var casas = parseInt(el.getAttribute("data-decimals") || "0", 10);
    var duracao = 1500;
    var inicio = null;
    var passo = function (t) {
      if (!inicio) inicio = t;
      var p = Math.min((t - inicio) / duracao, 1);
      var suave = 1 - Math.pow(1 - p, 3);
      el.textContent = formatar(alvo * suave, casas);
      if (p < 1) requestAnimationFrame(passo);
      else el.textContent = formatar(alvo, casas);
    };
    requestAnimationFrame(passo);
  };
  var contadores = document.querySelectorAll("[data-count]");
  if (contadores.length && "IntersectionObserver" in window && !reduzMovimento) {
    var ioC = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (en.isIntersecting) {
          contar(en.target);
          ioC.unobserve(en.target);
        }
      });
    }, { threshold: 0.6 });
    contadores.forEach(function (el) { ioC.observe(el); });
  }

  /* ---------- Galeria: filtros + lightbox ---------- */
  var galeria = document.querySelector("[data-gallery]");
  if (galeria) {
    var itens = Array.prototype.slice.call(galeria.querySelectorAll(".g-item"));
    var botoes = document.querySelectorAll(".filter-btn");
    var status = document.getElementById("gallery-status");

    var aplicarFiltro = function (cat, rotulo) {
      var n = 0;
      itens.forEach(function (it) {
        var mostra = cat === "todos" || it.getAttribute("data-cat") === cat;
        it.hidden = !mostra;
        if (mostra) n++;
      });
      botoes.forEach(function (b) { b.setAttribute("aria-pressed", String(b.getAttribute("data-filter") === cat)); });
      if (status) status.textContent = "Mostrando " + n + " fotos" + (cat === "todos" ? "" : " de " + rotulo) + ".";
    };
    botoes.forEach(function (b) {
      b.addEventListener("click", function () {
        var cat = b.getAttribute("data-filter");
        aplicarFiltro(cat, b.getAttribute("data-label"));
        if (history.replaceState) history.replaceState(null, "", cat === "todos" ? location.pathname : "#" + cat);
      });
    });
    var filtrarPeloHash = function () {
      var hash = (location.hash || "").replace("#", "");
      var botao = document.querySelector('.filter-btn[data-filter="' + hash + '"]');
      if (botao) aplicarFiltro(hash, botao.getAttribute("data-label"));
    };
    filtrarPeloHash();
    window.addEventListener("hashchange", filtrarPeloHash);

    var dialog = document.getElementById("lightbox");
    if (dialog && typeof dialog.showModal === "function") {
      var img = dialog.querySelector("img");
      var legenda = dialog.querySelector("figcaption");
      var contador = dialog.querySelector(".lb-count");
      var visiveis = [];
      var atual = 0;
      var origem = null;

      var mostrar = function (i) {
        atual = (i + visiveis.length) % visiveis.length;
        var link = visiveis[atual].querySelector("a");
        var foto = link.querySelector("img");
        img.src = link.getAttribute("href");
        img.alt = foto.alt;
        legenda.textContent = foto.alt;
        contador.textContent = "Foto " + (atual + 1) + " de " + visiveis.length;
      };
      galeria.addEventListener("click", function (e) {
        var link = e.target.closest(".g-item a");
        if (!link) return;
        e.preventDefault();
        visiveis = itens.filter(function (it) { return !it.hidden; });
        origem = link;
        mostrar(visiveis.indexOf(link.parentElement));
        dialog.showModal();
        dialog.querySelector(".lb-close").focus();
      });
      dialog.querySelector(".lb-prev").addEventListener("click", function () { mostrar(atual - 1); });
      dialog.querySelector(".lb-next").addEventListener("click", function () { mostrar(atual + 1); });
      dialog.querySelector(".lb-close").addEventListener("click", function () { dialog.close(); });
      dialog.addEventListener("keydown", function (e) {
        if (e.key === "ArrowLeft") { e.preventDefault(); mostrar(atual - 1); }
        if (e.key === "ArrowRight") { e.preventDefault(); mostrar(atual + 1); }
      });
      dialog.addEventListener("click", function (e) {
        if (e.target === dialog || e.target.classList.contains("lb-stage")) dialog.close();
      });
      dialog.addEventListener("close", function () {
        img.src = "data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7";
        if (origem) origem.focus();
      });
      var toqueX = null;
      dialog.addEventListener("touchstart", function (e) { toqueX = e.touches[0].clientX; }, { passive: true });
      dialog.addEventListener("touchend", function (e) {
        if (toqueX === null) return;
        var dx = e.changedTouches[0].clientX - toqueX;
        if (Math.abs(dx) > 50) mostrar(atual + (dx < 0 ? 1 : -1));
        toqueX = null;
      });
    }
  }

  /* ---------- Formulário de orçamento → WhatsApp ---------- */
  var form = document.getElementById("form-orcamento");
  if (form) {
    var dataBR = function (v) {
      if (!v) return "";
      var p = v.split("-");
      return p.length === 3 ? p[2] + "/" + p[1] + "/" + p[0] : v;
    };
    var erroDatas = document.getElementById("erro-datas");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var de = form.elements["data_inicio"];
      var ate = form.elements["data_fim"];
      erroDatas.textContent = "";
      ate.removeAttribute("aria-invalid");
      if (de.value && ate.value && ate.value < de.value) {
        erroDatas.textContent = "A data final precisa ser depois da data inicial.";
        ate.setAttribute("aria-invalid", "true");
        ate.focus();
        return;
      }
      if (!form.checkValidity()) {
        form.reportValidity();
        return;
      }
      var v = function (n) { return (form.elements[n].value || "").trim(); };
      var linhas = [
        "Olá! Vi o site e gostaria de um orçamento.",
        "",
        "• Meu nome: " + v("nome"),
        "• Nome do pet: " + v("pet"),
        "• Porte: " + v("porte"),
        "• Serviço: " + v("servico")
      ];
      if (de.value || ate.value) {
        var periodo = de.value && ate.value ? dataBR(de.value) + " a " + dataBR(ate.value) : dataBR(de.value || ate.value);
        linhas.push("• Datas: " + periodo);
      }
      if (v("obs")) linhas.push("• Observações: " + v("obs"));
      var url = "https://wa.me/" + WHATSAPP + "?text=" + encodeURIComponent(linhas.join("\n"));
      var janela = window.open(url, "_blank");
      if (janela) janela.opener = null;
      else window.location.href = url;
    });
  }
})();
