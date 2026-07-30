const c = window.RCI;
document.getElementById("dl").href = c.pdfUrl;
document.getElementById("src").href = c.sourceUrl;
document.getElementById("repo").href = c.repoUrl;
document.getElementById("sha").textContent = c.pdfSha256;
document.getElementById("dl-size").textContent = `(${c.pdfSize})`;

document.getElementById("toc").innerHTML = window.RCI_BAB.map(
  (b) => `<li><a href="baca.html#p=${b.p}"><span>${b.t}</span><span>ms. ${b.p}</span></a></li>`
).join("");

const io = new IntersectionObserver(
  (entries) =>
    entries.forEach((e) => e.isIntersecting && (e.target.classList.add("is-in"), io.unobserve(e.target))),
  { rootMargin: "0px 0px -10% 0px" }
);
document.querySelectorAll(".reveal").forEach((n) => io.observe(n));
