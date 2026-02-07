const year = document.getElementById("year");

if (year) {
  year.textContent = new Date().getFullYear();
}

const customizerSection = document.getElementById("customizer");

if (customizerSection) {
  const floorTypeSelect = document.getElementById("floorType");
  const coatingOptions = document.querySelectorAll("[data-coating]");
  const colorOptionsContainer = document.getElementById("colorOptions");
  const additiveGrip = document.getElementById("additiveGrip");
  const additiveGloss = document.getElementById("additiveGloss");
  const selectionSummary = document.getElementById("selectionSummary");
  const previewCanvas = document.getElementById("floorPreview");
  const ctx = previewCanvas ? previewCanvas.getContext("2d") : null;

  if (
    !previewCanvas ||
    !ctx ||
    !floorTypeSelect ||
    !colorOptionsContainer ||
    !additiveGrip ||
    !additiveGloss ||
    !selectionSummary
  ) {
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

  const floorTypeLabels = {
    "residential-garage": "Residential garage",
    "commercial-garage": "Commercial garage",
    warehouse: "Warehouse",
    "aircraft-hangar": "Aircraft hangar",
    "commercial-kitchen": "Commercial kitchen",
    "outdoor-patio": "Outdoor patio",
  };

  const coatingLabels = {
    solid: "Solid color polyaspartic",
    flake: "Polyaspartic flake system",
    "solid-texture": "Solid color + texture additive",
  };

  const floorTypeStyles = {
    "residential-garage": {
      wallTop: "#eef2f7",
      wallBottom: "#cbd5e0",
      accent: "#dde5ee",
      light: 1,
    },
    "commercial-garage": {
      wallTop: "#e9edf3",
      wallBottom: "#c4ccd6",
      accent: "#d6dde6",
      light: 0.96,
    },
    warehouse: {
      wallTop: "#ececec",
      wallBottom: "#cfd6dc",
      accent: "#dde3ea",
      light: 0.92,
    },
    "aircraft-hangar": {
      wallTop: "#f0f3f7",
      wallBottom: "#d2dae4",
      accent: "#e1e8f0",
      light: 1.02,
    },
    "commercial-kitchen": {
      wallTop: "#f7f7f7",
      wallBottom: "#d7dde4",
      accent: "#e6edf5",
      light: 1.06,
      grid: true,
    },
    "outdoor-patio": {
      wallTop: "#d8ecff",
      wallBottom: "#c5d7e6",
      accent: "#e7f2ff",
      light: 1,
      sun: true,
    },
  };

  const state = {
    floorType: floorTypeSelect.value,
    coating: "solid",
    color: colorOptions[0],
    grip: additiveGrip.checked,
    gloss: additiveGloss.checked,
  };

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

  coatingOptions.forEach((button) => {
    button.addEventListener("click", () => {
      coatingOptions.forEach((item) => item.classList.remove("is-active"));
      button.classList.add("is-active");
      state.coating = button.dataset.coating;
      render();
    });
  });

  floorTypeSelect.addEventListener("change", (event) => {
    state.floorType = event.target.value;
    render();
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
    selectionSummary.textContent = `${floorTypeLabels[state.floorType]} · ${coatingLabels[state.coating]} · ${state.color.name} · ${additiveText}`;
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

  function drawBackground(width, height, style) {
    const wallGradient = ctx.createLinearGradient(0, 0, 0, height * 0.55);
    wallGradient.addColorStop(0, style.wallTop);
    wallGradient.addColorStop(1, style.wallBottom);
    ctx.fillStyle = wallGradient;
    ctx.fillRect(0, 0, width, height);

    if (style.sun) {
      const sun = ctx.createRadialGradient(width * 0.82, height * 0.1, 10, width * 0.82, height * 0.1, height * 0.5);
      sun.addColorStop(0, "rgba(255, 255, 255, 0.6)");
      sun.addColorStop(1, "rgba(255, 255, 255, 0)");
      ctx.fillStyle = sun;
      ctx.fillRect(0, 0, width, height * 0.6);
    }

    ctx.fillStyle = style.accent;
    ctx.fillRect(0, height * 0.45, width, height * 0.02);

    if (style.grid) {
      ctx.strokeStyle = "rgba(11, 31, 58, 0.08)";
      ctx.lineWidth = 1;
      for (let x = 0; x <= width; x += 60) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height * 0.45);
        ctx.stroke();
      }
    }
  }

  function drawFloor(width, height, style) {
    const floor = {
      x1: width * 0.04,
      y1: height * 0.95,
      x2: width * 0.96,
      y2: height * 0.95,
      x3: width * 0.68,
      y3: height * 0.45,
      x4: width * 0.32,
      y4: height * 0.45,
    };

    ctx.save();
    ctx.beginPath();
    ctx.moveTo(floor.x1, floor.y1);
    ctx.lineTo(floor.x2, floor.y2);
    ctx.lineTo(floor.x3, floor.y3);
    ctx.lineTo(floor.x4, floor.y4);
    ctx.closePath();
    ctx.clip();

    const base = state.color.hex;
    const gradient = ctx.createLinearGradient(0, floor.y1, 0, floor.y3);
    gradient.addColorStop(0, shadeColor(base, 0.12 * style.light));
    gradient.addColorStop(1, shadeColor(base, -0.2));
    ctx.fillStyle = gradient;
    ctx.fillRect(0, floor.y3, width, floor.y1 - floor.y3);

    if (state.coating === "flake") {
      drawFlakes(width, height, floor, base);
    }

    if (state.coating === "solid-texture" || state.grip) {
      drawGrit(width, height, floor, base);
    }

    drawGloss(width, height, floor);

    ctx.restore();

    ctx.strokeStyle = "rgba(11, 31, 58, 0.18)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(floor.x4, floor.y4);
    ctx.lineTo(floor.x3, floor.y3);
    ctx.stroke();
  }

  function drawFlakes(width, height, floor, base) {
    const seed = hashString(`${state.floorType}-${base}-flake`);
    const random = mulberry32(seed);
    const flakeColors = [
      shadeColor(base, 0.4),
      shadeColor(base, -0.35),
      "#ffffff",
      "#2f3a45",
    ];
    const count = 480;
    ctx.globalAlpha = 0.8;
    for (let i = 0; i < count; i += 1) {
      const x = floor.x1 + random() * (floor.x2 - floor.x1);
      const y = floor.y3 + random() * (floor.y1 - floor.y3);
      const depth = (y - floor.y3) / (floor.y1 - floor.y3);
      const size = (random() * 1.6 + 0.6) * (0.6 + depth);
      ctx.fillStyle = flakeColors[Math.floor(random() * flakeColors.length)];
      ctx.beginPath();
      ctx.arc(x, y, size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  }

  function drawGrit(width, height, floor, base) {
    const seed = hashString(`${state.floorType}-${base}-grit-${state.coating}-${state.grip}`);
    const random = mulberry32(seed);
    const gritColors = [shadeColor(base, -0.3), shadeColor(base, 0.2), "#e8edf3"];
    const count = 900;
    ctx.globalAlpha = 0.2;
    for (let i = 0; i < count; i += 1) {
      const x = floor.x1 + random() * (floor.x2 - floor.x1);
      const y = floor.y3 + random() * (floor.y1 - floor.y3);
      const depth = (y - floor.y3) / (floor.y1 - floor.y3);
      const size = (random() * 1.2 + 0.3) * (0.5 + depth);
      ctx.fillStyle = gritColors[Math.floor(random() * gritColors.length)];
      ctx.fillRect(x, y, size, size);
    }
    ctx.globalAlpha = 1;
  }

  function drawGloss(width, height, floor) {
    const glossStrength = state.gloss ? 0.35 : 0.18;
    const gloss = ctx.createLinearGradient(0, floor.y1, 0, floor.y3);
    gloss.addColorStop(0, `rgba(255, 255, 255, ${0.35 * glossStrength})`);
    gloss.addColorStop(0.35, `rgba(255, 255, 255, ${0.7 * glossStrength})`);
    gloss.addColorStop(1, "rgba(255, 255, 255, 0)");
    ctx.fillStyle = gloss;
    ctx.fillRect(0, floor.y3, width, floor.y1 - floor.y3);

    ctx.globalAlpha = glossStrength;
    ctx.beginPath();
    ctx.moveTo(width * 0.18, floor.y1 - 10);
    ctx.lineTo(width * 0.82, floor.y1 - 10);
    ctx.lineTo(width * 0.6, floor.y3 + 20);
    ctx.lineTo(width * 0.4, floor.y3 + 20);
    ctx.closePath();
    ctx.fillStyle = "rgba(255, 255, 255, 0.35)";
    ctx.fill();
    ctx.globalAlpha = 1;
  }

  function render() {
    resizeCanvas();
    const width = previewCanvas.width / (window.devicePixelRatio || 1);
    const height = previewCanvas.height / (window.devicePixelRatio || 1);
    const style = floorTypeStyles[state.floorType];
    ctx.clearRect(0, 0, width, height);
    drawBackground(width, height, style);
    drawFloor(width, height, style);
    updateSummary();
  }

  window.addEventListener("resize", render);
  render();
}
