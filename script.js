const year = document.getElementById("year");

if (year) {
  year.textContent = new Date().getFullYear();
}

const initCustomizer = () => {
  const customizerSection = document.getElementById("customizer");

  if (!customizerSection) {
    return;
  }

  const coatingOptions = document.querySelectorAll("[data-coating]");
  const colorOptionsContainer = document.getElementById("colorOptions");
  const chipOptionsContainer = document.getElementById("chipOptions");
  const solidColorGroup = document.getElementById("solidColorGroup");
  const chipColorGroup = document.getElementById("chipColorGroup");
  const additiveGrip = document.getElementById("additiveGrip");
  const additiveGloss = document.getElementById("additiveGloss");
  const selectionSummary = document.getElementById("selectionSummary");
  const previewCanvas = document.getElementById("floorPreview");
  const ctx = previewCanvas ? previewCanvas.getContext("2d") : null;

  const isCustomizerReady =
    previewCanvas &&
    ctx &&
    colorOptionsContainer &&
    chipOptionsContainer &&
    solidColorGroup &&
    chipColorGroup &&
    additiveGrip &&
    additiveGloss &&
    selectionSummary;

  if (!isCustomizerReady) {
    if (selectionSummary) {
      selectionSummary.textContent = "Preview unavailable in this browser.";
    }
    return;
  }

  const colorOptions = [
    { name: "Jet Black", hex: "#0b0c10" },
    { name: "Steel Gray", hex: "#7b7d81" },
    { name: "Graphite", hex: "#a2a5a9" },
    { name: "Stone Gray", hex: "#c7c9cc" },
    { name: "Sandstone", hex: "#e7d6c5" },
    { name: "Bone", hex: "#e8dfd1" },
    { name: "Clay", hex: "#b47b78" },
    { name: "Sky Blue", hex: "#6cc9f2" },
    { name: "Polar White", hex: "#ffffff" },
    { name: "Harbor Blue", hex: "#5b92a7" },
    { name: "Terracotta", hex: "#d47b76" },
    { name: "Sage Green", hex: "#8a9b7b" },
    { name: "Copper", hex: "#e29a62" },
    { name: "Sun Gold", hex: "#f2cf63" },
  ];

  const chipOptions = [
    {
      name: "Slate Drift",
      colors: ["#0b0c10", "#7b7d81", "#a2a5a9", "#c7c9cc"],
    },
    {
      name: "Coastal Mist",
      colors: ["#e8dfd1", "#c7c9cc", "#5b92a7", "#ffffff"],
    },
    {
      name: "Tuxedo",
      colors: ["#0b0c10", "#2f3a45", "#a2a5a9", "#ffffff"],
    },
    {
      name: "Desert Stone",
      colors: ["#e7d6c5", "#e29a62", "#c7c9cc", "#ffffff"],
    },
    {
      name: "Harbor Blend",
      colors: ["#5b92a7", "#7b7d81", "#c7c9cc", "#ffffff"],
    },
    {
      name: "Clay Ridge",
      colors: ["#b47b78", "#d47b76", "#e7d6c5", "#c7c9cc"],
    },
  ];

  const coatingLabels = {
    solid: "Solid color polyaspartic",
    flake: "Polyaspartic flake system",
    "solid-texture": "Solid color + texture additive",
  };

  const state = {
    coating: "solid",
    color: colorOptions[0],
    chip: chipOptions[0],
    grip: additiveGrip.checked,
    gloss: additiveGloss.checked,
  };

  function updateActiveColor(selectedHex) {
    const buttons = colorOptionsContainer.querySelectorAll(".color-option");
    buttons.forEach((button) => {
      if (button.dataset.color === selectedHex) {
        button.classList.add("is-active");
      } else {
        button.classList.remove("is-active");
      }
    });
  }

  function updateActiveChip(selectedName) {
    const buttons = chipOptionsContainer.querySelectorAll(".chip-option");
    buttons.forEach((button) => {
      if (button.dataset.name === selectedName) {
        button.classList.add("is-active");
      } else {
        button.classList.remove("is-active");
      }
    });
  }

  function updateCoatingUI() {
    const isFlake = state.coating === "flake";
    solidColorGroup.classList.toggle("is-hidden", isFlake);
    chipColorGroup.classList.toggle("is-hidden", !isFlake);

    if (state.coating === "solid-texture") {
      additiveGrip.checked = true;
      additiveGrip.disabled = true;
      state.grip = true;
    } else {
      additiveGrip.disabled = false;
      state.grip = additiveGrip.checked;
    }
  }

  function buildColorOptions() {
    colorOptionsContainer.innerHTML = "";
    colorOptions.forEach((option, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "color-option";
      button.style.background = option.hex;
      button.dataset.color = option.hex;
      button.dataset.name = option.name;
      button.setAttribute("aria-label", option.name);
      if (index === 0) {
        button.classList.add("is-active");
      }
      button.addEventListener("click", () => {
        state.color = option;
        updateActiveColor(option.hex);
        render();
      });
      colorOptionsContainer.appendChild(button);
    });
  }

  function buildChipOptions() {
    chipOptionsContainer.innerHTML = "";
    chipOptions.forEach((chip, index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "chip-option";
      button.style.setProperty("--chip-a", chip.colors[0]);
      button.style.setProperty("--chip-b", chip.colors[1]);
      button.style.setProperty("--chip-c", chip.colors[2]);
      button.style.setProperty("--chip-base-1", chip.colors[2]);
      button.style.setProperty("--chip-base-2", chip.colors[3]);
      button.dataset.name = chip.name;
      button.setAttribute("aria-label", chip.name);

      const swatch = document.createElement("span");
      swatch.className = "chip-swatch";
      const label = document.createElement("span");
      label.className = "chip-name";
      label.textContent = chip.name;

      button.appendChild(swatch);
      button.appendChild(label);

      if (index === 0) {
        button.classList.add("is-active");
      }

      button.addEventListener("click", () => {
        state.chip = chip;
        updateActiveChip(chip.name);
        render();
      });

      chipOptionsContainer.appendChild(button);
    });
  }

  coatingOptions.forEach((button) => {
    button.addEventListener("click", () => {
      coatingOptions.forEach((item) => item.classList.remove("is-active"));
      button.classList.add("is-active");
      state.coating = button.dataset.coating;
      updateCoatingUI();
      render();
    });
  });

  additiveGrip.addEventListener("change", (event) => {
    state.grip = event.target.checked;
    render();
  });

  additiveGloss.addEventListener("change", (event) => {
    state.gloss = event.target.checked;
    render();
  });

  function updateSummary() {
    const additives = [];
    if (state.coating === "solid-texture" || state.grip) {
      additives.push("Slip-resistant additive");
    }
    if (state.gloss) {
      additives.push("Extra gloss topcoat");
    }
    const additiveText = additives.length ? additives.join(", ") : "No additives";
    const colorLabel =
      state.coating === "flake" && state.chip
        ? state.chip.name
        : state.color.name;
    selectionSummary.textContent = `${coatingLabels[state.coating]} · ${colorLabel} · ${additiveText}`;
  }

  function hexToRgb(hex) {
    const sanitized = hex.replace("#", "");
    const bigint = parseInt(sanitized, 16);
    return {
      r: (bigint >> 16) & 255,
      g: (bigint >> 8) & 255,
      b: bigint & 255,
    };
  }

  function rgbToHex({ r, g, b }) {
    const toHex = (value) => value.toString(16).padStart(2, "0");
    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
  }

  function shadeColor(hex, percent) {
    const { r, g, b } = hexToRgb(hex);
    const target = percent < 0 ? 0 : 255;
    const p = Math.abs(percent);
    return rgbToHex({
      r: Math.round((target - r) * p + r),
      g: Math.round((target - g) * p + g),
      b: Math.round((target - b) * p + b),
    });
  }

  function hashString(value) {
    let hash = 2166136261;
    for (let i = 0; i < value.length; i += 1) {
      hash ^= value.charCodeAt(i);
      hash = Math.imul(hash, 16777619);
    }
    return hash >>> 0;
  }

  function mulberry32(seed) {
    return function random() {
      let t = (seed += 0x6d2b79f5);
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function resizeCanvas() {
    const rect = previewCanvas.getBoundingClientRect();
    const ratio = window.devicePixelRatio || 1;
    previewCanvas.width = rect.width * ratio;
    previewCanvas.height = rect.height * ratio;
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
  }

  function drawBase(width, height, baseColor) {
    const gradient = ctx.createLinearGradient(0, 0, width, height);
    gradient.addColorStop(0, shadeColor(baseColor, 0.18));
    gradient.addColorStop(0.6, baseColor);
    gradient.addColorStop(1, shadeColor(baseColor, -0.15));
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, width, height);

    ctx.globalAlpha = 0.12;
    ctx.fillStyle = "rgba(255, 255, 255, 0.6)";
    for (let i = 0; i < 4; i += 1) {
      ctx.beginPath();
      ctx.arc(width * (0.2 + i * 0.2), height * 0.2, width * 0.25, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  function drawFlakes(width, height, chip) {
    const seed = hashString(`${chip.name}-flake`);
    const random = mulberry32(seed);
    const count = 900;
    ctx.globalAlpha = 0.85;
    for (let i = 0; i < count; i += 1) {
      const x = random() * width;
      const y = random() * height;
      const size = random() * 2.4 + 0.6;
      ctx.fillStyle = chip.colors[Math.floor(random() * chip.colors.length)];
      ctx.beginPath();
      ctx.arc(x, y, size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  function drawGrit(width, height, base) {
    const seed = hashString(`${base}-grit-${state.coating}-${state.grip}`);
    const random = mulberry32(seed);
    const gritColors = [shadeColor(base, -0.3), shadeColor(base, 0.2), "#e8edf3"];
    const count = 1100;
    ctx.globalAlpha = 0.2;
    for (let i = 0; i < count; i += 1) {
      const x = random() * width;
      const y = random() * height;
      const size = random() * 1.6 + 0.4;
      ctx.fillStyle = gritColors[Math.floor(random() * gritColors.length)];
      ctx.fillRect(x, y, size, size);
    }
    ctx.globalAlpha = 1;
  }

  function drawGloss(width, height) {
    const glossStrength = state.gloss ? 0.35 : 0.15;
    const gloss = ctx.createLinearGradient(0, 0, width, height);
    gloss.addColorStop(0, `rgba(255, 255, 255, ${0.2 * glossStrength})`);
    gloss.addColorStop(0.4, `rgba(255, 255, 255, ${0.7 * glossStrength})`);
    gloss.addColorStop(1, "rgba(255, 255, 255, 0)");
    ctx.fillStyle = gloss;
    ctx.fillRect(0, 0, width, height);

    ctx.globalAlpha = glossStrength;
    ctx.beginPath();
    ctx.moveTo(width * 0.1, height * 0.1);
    ctx.lineTo(width * 0.9, height * 0.2);
    ctx.lineTo(width * 0.8, height * 0.35);
    ctx.lineTo(width * 0.2, height * 0.25);
    ctx.closePath();
    ctx.fillStyle = "rgba(255, 255, 255, 0.35)";
    ctx.fill();
    ctx.globalAlpha = 1;
  }

  function render() {
    resizeCanvas();
    const width = previewCanvas.width / (window.devicePixelRatio || 1);
    const height = previewCanvas.height / (window.devicePixelRatio || 1);
    ctx.clearRect(0, 0, width, height);

    const baseColor =
      state.coating === "flake" && state.chip
        ? state.chip.colors[1]
        : state.color.hex;

    drawBase(width, height, baseColor);

    if (state.coating === "flake" && state.chip) {
      drawFlakes(width, height, state.chip);
    }

    if (state.coating === "solid-texture" || state.grip) {
      drawGrit(width, height, baseColor);
    }

    drawGloss(width, height);
    updateSummary();
  }

  buildColorOptions();
  buildChipOptions();
  updateCoatingUI();
  selectionSummary.textContent = "Preview ready. Choose options above.";
  window.addEventListener("resize", render);
  window.requestAnimationFrame(render);
};

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initCustomizer);
} else {
  initCustomizer();
}
