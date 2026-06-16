document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".tool-card, .feature-card, .note-card").forEach((card) => {
    card.addEventListener("mouseenter", () => card.classList.add("shadow-lg"));
    card.addEventListener("mouseleave", () => card.classList.remove("shadow-lg"));
  });

  const yearNode = document.querySelector("#year");
  if (yearNode) yearNode.textContent = new Date().getFullYear();
});

document.querySelectorAll(".ai-suggestions button")
.forEach(btn => {

    btn.addEventListener("click", () => {

        document.querySelector(
          'input[name="question"]'
        ).value = btn.innerText;

    });

});
