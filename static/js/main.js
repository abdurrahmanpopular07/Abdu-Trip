(function () {
  "use strict";

  // ---- destinations data (also used as the source-city dataset) ----------
  const DESTINATIONS = JSON.parse(document.getElementById("destinations-data").textContent);
  const destEntries = Object.entries(DESTINATIONS); // [key, {label, state}]

  const form = document.getElementById("plan-form");
  const generateBtn = document.getElementById("generate-btn");
  const formError = document.getElementById("form-error");
  const resultsSection = document.getElementById("results");
  const replanBtn = document.getElementById("replan-btn");
  const printBtn = document.getElementById("print-btn");

  const rupee = (n) => "\u20B9" + Number(n).toLocaleString("en-IN");

  // ---- generic autocomplete wiring ----------------------------------------
  function setupAutocomplete(inputEl, hiddenEl, listEl, onPick) {
    let activeIndex = -1;
    let currentMatches = [];

    function render(matches) {
      currentMatches = matches;
      activeIndex = -1;
      if (!matches.length) {
        listEl.innerHTML = '<div class="autocomplete-empty">No matches — try a different spelling.</div>';
        listEl.hidden = false;
        return;
      }
      listEl.innerHTML = matches
        .map((m, i) => `<div class="autocomplete-item" data-index="${i}">${m[1].label}<span class="ac-state">${m[1].state}</span></div>`)
        .join("");
      listEl.hidden = false;
    }

    function pick(match) {
      inputEl.value = `${match[1].label} (${match[1].state})`;
      hiddenEl.value = match[0];
      listEl.hidden = true;
      if (onPick) onPick(match);
    }

    inputEl.addEventListener("input", () => {
      hiddenEl.value = "";
      const q = inputEl.value.trim().toLowerCase();
      if (!q) { listEl.hidden = true; return; }
      const matches = destEntries.filter(
        ([, d]) => d.label.toLowerCase().includes(q) || d.state.toLowerCase().includes(q)
      ).slice(0, 8);
      render(matches);
    });

    inputEl.addEventListener("focus", () => {
      if (inputEl.value.trim()) inputEl.dispatchEvent(new Event("input"));
    });

    inputEl.addEventListener("keydown", (e) => {
      if (listEl.hidden || !currentMatches.length) return;
      if (e.key === "ArrowDown") {
        e.preventDefault();
        activeIndex = Math.min(activeIndex + 1, currentMatches.length - 1);
        updateActive();
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        activeIndex = Math.max(activeIndex - 1, 0);
        updateActive();
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (activeIndex >= 0) pick(currentMatches[activeIndex]);
      } else if (e.key === "Escape") {
        listEl.hidden = true;
      }
    });

    function updateActive() {
      [...listEl.children].forEach((el, i) => el.classList.toggle("is-active", i === activeIndex));
    }

    listEl.addEventListener("click", (e) => {
      const item = e.target.closest(".autocomplete-item");
      if (!item) return;
      const idx = Number(item.dataset.index);
      pick(currentMatches[idx]);
    });

    document.addEventListener("click", (e) => {
      if (!inputEl.contains(e.target) && !listEl.contains(e.target)) listEl.hidden = true;
    });
  }

  const destInput = document.getElementById("destination-input");
  const destHidden = document.getElementById("destination");
  const destList = document.getElementById("destination-list");
  setupAutocomplete(destInput, destHidden, destList);

  const sourceInput = document.getElementById("source-input");
  const sourceKeyHidden = document.getElementById("source-key");
  const sourceList = document.getElementById("source-list");
  const sourceLatHidden = document.getElementById("source-lat");
  const sourceLonHidden = document.getElementById("source-lon");
  const sourceStatus = document.getElementById("source-status");
  const locationBtn = document.getElementById("use-location-btn");

  setupAutocomplete(sourceInput, sourceKeyHidden, sourceList, () => {
    // Manual pick overrides any GPS coordinates captured earlier.
    sourceLatHidden.value = "";
    sourceLonHidden.value = "";
    locationBtn.classList.remove("is-active");
    sourceStatus.textContent = "Starting point set from your search.";
  });

  locationBtn.addEventListener("click", () => {
    if (!navigator.geolocation) {
      sourceStatus.textContent = "Geolocation isn't supported here — please search your city instead.";
      return;
    }
    sourceStatus.textContent = "Detecting your location...";
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        sourceLatHidden.value = pos.coords.latitude;
        sourceLonHidden.value = pos.coords.longitude;
        sourceKeyHidden.value = "";
        sourceInput.value = "";
        locationBtn.classList.add("is-active");
        sourceStatus.textContent = "Location detected \u2713 — using your current position.";
      },
      () => {
        sourceStatus.textContent = "Location access denied — please search your city below instead.";
      },
      { timeout: 8000 }
    );
  });

  function setLoading(isLoading) {
    generateBtn.disabled = isLoading;
    generateBtn.classList.toggle("is-loading", isLoading);
  }

  function showError(message) {
    formError.textContent = message;
  }

  function clearError() {
    formError.textContent = "";
  }

  function animateBar(el, pct) {
    requestAnimationFrame(() => {
      el.style.width = Math.min(100, Math.max(4, pct)) + "%";
    });
  }

  const STATUS_COPY = {
    surplus:     { color: "var(--green)" },
    comfortable: { color: "var(--green)" },
    shortfall:   { color: "var(--coral)" },
  };

  function renderResults(data) {
    document.getElementById("result-eyebrow").textContent =
      `${data.days}-day ${data.style} trip \u00B7 from ${data.source_label}`;
    document.getElementById("result-title").textContent = `Your ${data.destination} plan`;
    document.getElementById("model-note").textContent =
      `Cost model R\u00B2 ${data.model_metrics.r2.toFixed(2)} on held-out test data \u00B7 estimate, not a live quote`;

    // AI-generated destination image
    const img = document.getElementById("destination-image");
    const skeleton = document.getElementById("dest-image-skeleton");
    img.hidden = true;
    skeleton.hidden = false;
    img.onload = () => { skeleton.hidden = true; img.hidden = false; };
    img.onerror = () => { skeleton.hidden = true; img.hidden = true; };
    img.alt = `AI-generated view of ${data.destination}`;
    img.src = data.image_url;

    const budget = data.budget;
    const totalRequired = data.total_required;
    const maxVal = Math.max(budget, totalRequired) || 1;

    document.getElementById("val-budget").textContent = rupee(budget);
    document.getElementById("val-estimate").textContent = rupee(totalRequired);
    animateBar(document.getElementById("bar-budget"), (budget / maxVal) * 100);
    animateBar(document.getElementById("bar-estimate"), (totalRequired / maxVal) * 100);

    const verdict = document.getElementById("cost-verdict");
    const diff = Math.abs(budget - totalRequired);
    if (data.budget_status === "surplus") {
      verdict.textContent = `You have solid surplus \u2014 about ${rupee(diff)} more than this trip typically needs.`;
    } else if (data.budget_status === "comfortable") {
      verdict.textContent = `Comfortably within budget \u2014 about ${rupee(diff)} of headroom.`;
    } else {
      verdict.textContent = `Running about ${rupee(diff)} short of the typical requirement \u2014 see the notes below.`;
    }
    verdict.style.color = STATUS_COPY[data.budget_status]?.color || "var(--ink)";

    // Travel card
    document.getElementById("travel-route").textContent =
      `${data.source_label} \u2192 ${data.destination} by ${data.travel_mode}`;
    document.getElementById("travel-distance").textContent = data.distance_km.toLocaleString("en-IN");
    document.getElementById("travel-cost-num").textContent = rupee(data.travel_cost);
    document.getElementById("travel-detail").textContent = data.travel_detail;

    const breakdownList = document.getElementById("breakdown-list");
    breakdownList.innerHTML = "";
    const labelOverrides = { intercity_travel: "Intercity travel", local_transport: "Local transport" };
    Object.entries(data.budget_breakdown).forEach(([category, amount]) => {
      const li = document.createElement("li");
      const label = labelOverrides[category] || category;
      li.innerHTML = `<span class="breakdown-cat">${label}</span><span class="breakdown-amt">${rupee(amount)}</span>`;
      breakdownList.appendChild(li);
    });

    // Destination highlights
    document.getElementById("highlights-title").textContent = `Highlights of ${data.destination}`;
    const foodChips = document.getElementById("food-chips");
    foodChips.innerHTML = data.famous_food.map((f) => `<span class="chip">${f}</span>`).join("");
    const thingsChips = document.getElementById("things-chips");
    thingsChips.innerHTML = data.famous_things.map((t) => `<span class="chip">${t}</span>`).join("");

    const itineraryList = document.getElementById("itinerary-list");
    itineraryList.innerHTML = "";
    data.itinerary.forEach((day) => {
      const card = document.createElement("div");
      card.className = "day-card";
      card.innerHTML = `
        <div class="day-num">DAY<br>${String(day.day).padStart(2, "0")}</div>
        <div>
          <div class="day-theme">${day.theme}</div>
          <div class="day-slots">
            <div><span class="day-slot-label">Morning</span><span class="day-slot-text">${day.morning}</span></div>
            <div><span class="day-slot-label">Afternoon</span><span class="day-slot-text">${day.afternoon}</span></div>
            <div><span class="day-slot-label">Evening</span><span class="day-slot-text">${day.evening}</span></div>
          </div>
        </div>`;
      itineraryList.appendChild(card);
    });

    const tipsList = document.getElementById("tips-list");
    tipsList.innerHTML = "";
    data.tips.forEach((tip) => {
      const li = document.createElement("li");
      li.textContent = tip;
      tipsList.appendChild(li);
    });

    resultsSection.hidden = false;
    resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError();

    const destination = destHidden.value;
    const days = document.getElementById("days").value;
    const budget = document.getElementById("budget").value;
    const style = form.querySelector('input[name="style"]:checked').value;
    const travelMode = form.querySelector('input[name="travel_mode"]:checked').value;
    const sourceKey = sourceKeyHidden.value;
    const sourceLat = sourceLatHidden.value;
    const sourceLon = sourceLonHidden.value;

    if (!destination) {
      showError("Search and pick a destination from the list to continue.");
      return;
    }
    if (!sourceKey && !(sourceLat && sourceLon)) {
      showError("Share your starting point — tap \u201CUse my current location\u201D or search your city.");
      return;
    }
    if (!days || Number(days) < 1 || Number(days) > 21) {
      showError("Days should be between 1 and 21.");
      return;
    }
    if (!budget || Number(budget) < 1000) {
      showError("Budget should be at least \u20B91,000.");
      return;
    }

    setLoading(true);
    try {
      const res = await fetch("/api/plan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          destination, days, budget, style,
          travel_mode: travelMode,
          source_key: sourceKey,
          source_lat: sourceLat || null,
          source_lon: sourceLon || null,
        }),
      });
      const data = await res.json();

      if (!res.ok) {
        if (data.login_required) {
          window.location.href = "/login?next=" + encodeURIComponent(window.location.pathname) + "%23plan";
          return;
        }
        showError(data.error || "Something went wrong. Please try again.");
        return;
      }
      renderResults(data);
    } catch (err) {
      showError("Couldn't reach the planner. Check your connection and try again.");
    } finally {
      setLoading(false);
    }
  });

  replanBtn.addEventListener("click", () => {
    resultsSection.hidden = true;
    document.getElementById("planner-card").scrollIntoView({ behavior: "smooth", block: "center" });
  });

  printBtn.addEventListener("click", () => window.print());
})();
