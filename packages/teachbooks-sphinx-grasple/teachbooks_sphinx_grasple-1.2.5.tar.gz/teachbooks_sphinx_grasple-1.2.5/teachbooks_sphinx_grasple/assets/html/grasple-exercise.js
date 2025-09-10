document.addEventListener("DOMContentLoaded", () => {

  // Check if fullscreenbackground already exists
  if (!document.querySelector(".fullscreenbackground")) {
    const bg = document.createElement("div");
    bg.className = "fullscreenbackground";
    document.body.appendChild(bg);
  }

  function updateFullscreenButtons() {
    document.querySelectorAll(".admonition.fullscreenable").forEach(admonition => {
      const header = admonition.querySelector("p.admonition-title");
      if (!header) return;
      // Remove existing button(s)
      header.querySelectorAll(".fullscreen-btn").forEach(btn => btn.remove());
      // Only add button if not high-contrast
      if (!document.body.classList.contains("high-contrast")) {
        const btn = document.createElement("button");
        btn.className = "fullscreen-btn";
        btn.innerHTML = '<i class="fas fa-maximize"></i>';
        btn.onclick = function () {
          const bg = document.querySelector(".fullscreenbackground");
          const details = admonition.querySelector("section details");
          if (admonition.classList.contains("fullscreen")) {
            admonition.classList.remove("fullscreen");
            const grasple = details.querySelector(".grasplecontainer");
            grasple.style.height = `400px`;
            btn.innerHTML = '<i class="fas fa-maximize"></i>';
            if (bg) bg.classList.remove("active");
          } else {
            btn.innerHTML = '<i class="fas fa-minimize"></i>';
            admonition.classList.add("fullscreen");
            // Open details if not already open
            if (details && !details.hasAttribute("open")) {
              details.setAttribute("open", "");
            }
            if (details) {
              // Measure available height
              const detailsRect = admonition.getBoundingClientRect();
              const summary = details.querySelector("summary");
              const summaryRect = summary.getBoundingClientRect();
              const remainder = detailsRect.height - summaryRect.bottom;
              const grasple = details.querySelector(".grasplecontainer");
              grasple.style.height = `calc(${remainder}px + 1.5rem)`;
            }
            if (bg) bg.classList.add("active");
          }
        };
        // Style the button into the title bar
        header.style.position = "relative";
        btn.style.position = "absolute";
        btn.style.right = "0.5em";
        btn.style.top = "0.2em";
        header.appendChild(btn);
      }
    });
  }

  // Initial setup
  updateFullscreenButtons();

  // Watch for changes to body classList
  const observer = new MutationObserver(mutations => {
    mutations.forEach(mutation => {
      if (mutation.type === "attributes" && mutation.attributeName === "class") {
        updateFullscreenButtons();
      }
    });
  });
  observer.observe(document.body, { attributes: true });
});
