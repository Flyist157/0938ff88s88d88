const roleContent = {
  pro: {
    title: "Preview every lead and pay only when you accept it.",
    description:
      "LeadPilot matches customers with pros in minutes. Pros see the job details, price, and expected response time before deciding to accept or decline.",
    primaryCta: "Join as a pro",
    secondaryCta: "See lead pricing",
    badge: "Pay only on accepted leads",
  },
  customer: {
    title: "Get matched with trusted pros who respond fast.",
    description:
      "Customers post a job once and receive responses from available pros. Pros only accept work that fits their schedule, so you get faster replies.",
    primaryCta: "Post a job",
    secondaryCta: "Browse top pros",
    badge: "Get up to 5 quotes fast",
  },
};

const roleButtons = document.querySelectorAll("[data-role]");
const heroTitle = document.getElementById("hero-title");
const heroDescription = document.getElementById("hero-description");
const primaryCta = document.getElementById("primary-cta");
const secondaryCta = document.getElementById("secondary-cta");
const heroBadge = document.getElementById("hero-badge");

const updateRole = (role) => {
  const content = roleContent[role];
  if (!content) {
    return;
  }

  roleButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.role === role);
  });

  heroTitle.textContent = content.title;
  heroDescription.textContent = content.description;
  primaryCta.textContent = content.primaryCta;
  secondaryCta.textContent = content.secondaryCta;
  heroBadge.textContent = content.badge;
};

roleButtons.forEach((button) => {
  button.addEventListener("click", () => updateRole(button.dataset.role));
});

const leadsSeed = [
  {
    id: 1,
    title: "Kitchen sink repair",
    location: "Austin, TX",
    budget: "$120 to $180",
    response: "Respond in 1 hour",
    price: 18,
  },
  {
    id: 2,
    title: "Fence replacement quote",
    location: "Round Rock, TX",
    budget: "$800 to $1,200",
    response: "Respond in 3 hours",
    price: 32,
  },
  {
    id: 3,
    title: "Weekly lawn care",
    location: "Pflugerville, TX",
    budget: "$120 per month",
    response: "Respond in 6 hours",
    price: 14,
  },
];

const leadList = document.getElementById("lead-list");
const leadLog = document.getElementById("lead-log");
const activeCount = document.getElementById("active-count");
const acceptedCount = document.getElementById("accepted-count");
const declinedCount = document.getElementById("declined-count");
const totalDue = document.getElementById("total-due");
const resetDemo = document.getElementById("reset-demo");

let leadState = {
  active: [...leadsSeed],
  accepted: [],
  declined: [],
};

const formatCurrency = (value) => `$${value.toFixed(0)}`;

const updateStats = () => {
  activeCount.textContent = leadState.active.length;
  acceptedCount.textContent = leadState.accepted.length;
  declinedCount.textContent = leadState.declined.length;

  const total = leadState.accepted.reduce((sum, lead) => sum + lead.price, 0);
  totalDue.textContent = formatCurrency(total);
};

const addLogEntry = (type, lead) => {
  const entry = document.createElement("li");
  entry.textContent = `${type}: ${lead.title} - ${formatCurrency(
    lead.price
  )} lead`;
  leadLog.prepend(entry);
};

const renderLeads = () => {
  leadList.innerHTML = "";

  if (leadState.active.length === 0) {
    const empty = document.createElement("p");
    empty.className = "note";
    empty.textContent = "No new leads. Reset the demo to view more.";
    leadList.appendChild(empty);
    return;
  }

  leadState.active.forEach((lead) => {
    const card = document.createElement("div");
    card.className = "lead-card";

    const title = document.createElement("h4");
    title.textContent = lead.title;
    card.appendChild(title);

    const details = document.createElement("p");
    details.textContent = `${lead.location} - ${lead.budget}`;
    card.appendChild(details);

    const response = document.createElement("p");
    response.className = "subtle";
    response.textContent = lead.response;
    card.appendChild(response);

    const price = document.createElement("p");
    price.innerHTML = `<span class="label">Lead price</span> <strong>${formatCurrency(
      lead.price
    )}</strong>`;
    card.appendChild(price);

    const actions = document.createElement("div");
    actions.className = "lead-actions";

    const accept = document.createElement("button");
    accept.className = "button primary";
    accept.textContent = "Accept";
    accept.addEventListener("click", () => handleLeadAction("Accepted", lead.id));

    const decline = document.createElement("button");
    decline.className = "button ghost";
    decline.textContent = "Decline";
    decline.addEventListener("click", () =>
      handleLeadAction("Declined", lead.id)
    );

    actions.appendChild(accept);
    actions.appendChild(decline);
    card.appendChild(actions);

    leadList.appendChild(card);
  });
};

const handleLeadAction = (action, id) => {
  const leadIndex = leadState.active.findIndex((lead) => lead.id === id);
  if (leadIndex === -1) {
    return;
  }

  const [lead] = leadState.active.splice(leadIndex, 1);
  if (action === "Accepted") {
    leadState.accepted.push(lead);
  } else {
    leadState.declined.push(lead);
  }

  addLogEntry(action, lead);
  updateStats();
  renderLeads();
};

const resetLeadDemo = () => {
  leadState = {
    active: [...leadsSeed],
    accepted: [],
    declined: [],
  };
  leadLog.innerHTML = "";
  updateStats();
  renderLeads();
};

resetDemo.addEventListener("click", resetLeadDemo);

const profileFields = {
  name: document.getElementById("profile-name"),
  category: document.getElementById("profile-category"),
  area: document.getElementById("profile-area"),
  response: document.getElementById("profile-response"),
  acceptance: document.getElementById("profile-acceptance"),
  price: document.getElementById("profile-price"),
  bio: document.getElementById("profile-bio"),
};

const previewElements = {
  name: document.getElementById("preview-name"),
  category: document.getElementById("preview-category"),
  area: document.getElementById("preview-area"),
  response: document.getElementById("preview-response"),
  acceptance: document.getElementById("preview-acceptance"),
  price: document.getElementById("preview-price"),
  bio: document.getElementById("preview-bio"),
};

const applyText = (element, value) => {
  if (!element) {
    return;
  }
  const fallback = element.dataset.default || "";
  const nextValue = value && value.trim() ? value.trim() : fallback;
  element.textContent = nextValue;
};

const applyPrice = (element, value) => {
  if (!element) {
    return;
  }
  const fallback = element.dataset.default || "";
  const trimmed = value ? value.trim() : "";
  if (!trimmed) {
    element.textContent = fallback;
    return;
  }
  element.textContent = trimmed.startsWith("$") ? trimmed : `$${trimmed}`;
};

const updateProfilePreview = () => {
  if (!previewElements.name) {
    return;
  }
  applyText(previewElements.name, profileFields.name?.value);
  applyText(previewElements.category, profileFields.category?.value);
  applyText(previewElements.area, profileFields.area?.value);
  applyText(previewElements.response, profileFields.response?.value);
  applyText(previewElements.acceptance, profileFields.acceptance?.value);
  applyPrice(previewElements.price, profileFields.price?.value);
  applyText(previewElements.bio, profileFields.bio?.value);
};

Object.values(profileFields).forEach((field) => {
  if (!field) {
    return;
  }
  field.addEventListener("input", updateProfilePreview);
  field.addEventListener("change", updateProfilePreview);
});

updateProfilePreview();

const funnelInputs = {
  category: document.getElementById("funnel-category"),
  details: document.getElementById("funnel-details"),
  location: document.getElementById("funnel-location"),
  budget: document.getElementById("funnel-budget"),
  timeline: document.getElementById("funnel-timeline"),
  property: document.getElementById("funnel-property"),
  contact: document.getElementById("funnel-contact"),
};
const funnelSubmit = document.getElementById("funnel-submit");
const matchResults = document.getElementById("match-results");
const fullMatchCount = document.getElementById("full-match-count");
const partialMatchCount = document.getElementById("partial-match-count");

const proDirectory = [
  {
    id: 1,
    name: "Apex Plumbing Co.",
    categories: ["Plumbing"],
    serviceAreas: ["Austin, TX", "Round Rock, TX"],
    minBudget: 90,
    maxBudget: 600,
    responseTimeHours: 2,
    rating: 4.9,
    reviews: 45,
    acceptanceRate: "78%",
    startingPrice: "$120",
    tags: ["Verified", "Background checked"],
    propertyTypes: ["House", "Apartment"],
    keywords: ["sink", "faucet", "leak", "pipe"],
  },
  {
    id: 2,
    name: "Riverbend Landscaping",
    categories: ["Landscaping"],
    serviceAreas: ["Austin, TX", "Pflugerville, TX"],
    minBudget: 300,
    maxBudget: 2200,
    responseTimeHours: 8,
    rating: 4.7,
    reviews: 62,
    acceptanceRate: "82%",
    startingPrice: "$350",
    tags: ["Top rated", "Insured"],
    propertyTypes: ["House", "Commercial"],
    keywords: ["lawn", "irrigation", "mulch", "tree"],
  },
  {
    id: 3,
    name: "Sparkle Home Cleaners",
    categories: ["House cleaning"],
    serviceAreas: ["Austin, TX", "Cedar Park, TX"],
    minBudget: 120,
    maxBudget: 450,
    responseTimeHours: 4,
    rating: 4.8,
    reviews: 104,
    acceptanceRate: "90%",
    startingPrice: "$140",
    tags: ["Verified", "Eco-friendly"],
    propertyTypes: ["House", "Apartment"],
    keywords: ["deep clean", "move out", "kitchen", "bathroom"],
  },
  {
    id: 4,
    name: "Peak Performance Training",
    categories: ["Personal training"],
    serviceAreas: ["Austin, TX"],
    minBudget: 80,
    maxBudget: 500,
    responseTimeHours: 12,
    rating: 4.6,
    reviews: 29,
    acceptanceRate: "70%",
    startingPrice: "$95",
    tags: ["Certified", "Mobile"],
    propertyTypes: ["House", "Apartment"],
    keywords: ["strength", "weight loss", "fitness", "mobility"],
  },
  {
    id: 5,
    name: "Luxe Mobile Beauty",
    categories: ["Mobile beauty"],
    serviceAreas: ["Austin, TX", "Bee Cave, TX"],
    minBudget: 100,
    maxBudget: 900,
    responseTimeHours: 3,
    rating: 4.9,
    reviews: 58,
    acceptanceRate: "88%",
    startingPrice: "$150",
    tags: ["Top rated", "On-site"],
    propertyTypes: ["House", "Apartment", "Commercial"],
    keywords: ["hair", "makeup", "event", "wedding"],
  },
  {
    id: 6,
    name: "Bluebonnet Plumbing & Drain",
    categories: ["Plumbing"],
    serviceAreas: ["Austin, TX", "Kyle, TX"],
    minBudget: 150,
    maxBudget: 1500,
    responseTimeHours: 1,
    rating: 4.8,
    reviews: 76,
    acceptanceRate: "86%",
    startingPrice: "$175",
    tags: ["Emergency ready", "Verified"],
    propertyTypes: ["House", "Commercial"],
    keywords: ["drain", "clog", "water heater", "leak"],
  },
];

const budgetRanges = {
  "100-300": { min: 100, max: 300 },
  "300-800": { min: 300, max: 800 },
  "800-1500": { min: 800, max: 1500 },
  "1500-3000": { min: 1500, max: 3000 },
};

const timelineTargets = {
  "24h": 4,
  week: 24,
  flex: 72,
};

const normalize = (value) => (value || "").trim().toLowerCase();

const matchesLocation = (location, areas) => {
  const target = normalize(location);
  if (!target) {
    return false;
  }
  return areas.some((area) => {
    const normalizedArea = normalize(area);
    return normalizedArea.includes(target) || target.includes(normalizedArea);
  });
};

const matchesKeywords = (details, keywords) => {
  const text = normalize(details);
  if (!text) {
    return false;
  }
  return keywords.some((keyword) => text.includes(normalize(keyword)));
};

const buildMatchScore = (pro, criteria) => {
  const reasons = [];
  let score = 0;

  if (criteria.categoryMatch) {
    score += 40;
    reasons.push("Category");
  }

  if (criteria.locationMatch) {
    score += 25;
    reasons.push("Location");
  }

  if (criteria.budgetMatch) {
    score += 20;
    reasons.push("Budget");
  } else if (criteria.budgetNearMatch) {
    score += 10;
    reasons.push("Budget close");
  }

  if (criteria.timelineMatch) {
    score += 10;
    reasons.push("Response time");
  }

  if (criteria.propertyMatch) {
    score += 5;
    reasons.push("Property type");
  }

  if (criteria.keywordMatch) {
    score += 5;
    reasons.push("Project details");
  }

  score += Math.round(pro.rating * 2);

  return { score, reasons };
};

const buildMatchCard = (match) => {
  const card = document.createElement("div");
  card.className = "match-card";
  card.dataset.tier = match.isFull ? "full" : "partial";

  const header = document.createElement("div");
  header.className = "match-header";

  const info = document.createElement("div");
  const name = document.createElement("h4");
  name.textContent = match.pro.name;
  const subtitle = document.createElement("p");
  subtitle.className = "subtle";
  subtitle.textContent = `${match.pro.categories[0]} - ${match.pro.serviceAreas[0]}`;
  info.appendChild(name);
  info.appendChild(subtitle);

  const scoreWrap = document.createElement("div");
  const score = document.createElement("div");
  score.className = "match-score";
  score.textContent = `${match.percent}% match`;
  const status = document.createElement("div");
  status.className = "match-status";
  status.textContent = match.isFull ? "Full match" : "Partial match";
  scoreWrap.appendChild(score);
  scoreWrap.appendChild(status);

  header.appendChild(info);
  header.appendChild(scoreWrap);

  const tags = document.createElement("div");
  tags.className = "match-tags";
  match.pro.tags.forEach((tag) => {
    const badge = document.createElement("span");
    badge.className = "badge subtle";
    badge.textContent = tag;
    tags.appendChild(badge);
  });

  const meta = document.createElement("div");
  meta.className = "match-meta";
  meta.innerHTML = `
    <div>
      <span class="label">Response</span>
      <strong>Within ${match.pro.responseTimeHours} hours</strong>
    </div>
    <div>
      <span class="label">Acceptance</span>
      <strong>${match.pro.acceptanceRate}</strong>
    </div>
    <div>
      <span class="label">Starting at</span>
      <strong>${match.pro.startingPrice}</strong>
    </div>
  `;

  const reasons = document.createElement("p");
  reasons.className = "note";
  reasons.textContent = match.reasons.length
    ? `Matched on: ${match.reasons.join(", ")}.`
    : "Limited match based on availability.";

  const actions = document.createElement("div");
  actions.className = "match-actions";
  const viewButton = document.createElement("button");
  viewButton.className = "button primary";
  viewButton.textContent = "View profile";
  const requestButton = document.createElement("button");
  requestButton.className = "button ghost";
  requestButton.textContent = "Request quote";
  actions.appendChild(viewButton);
  actions.appendChild(requestButton);

  card.appendChild(header);
  card.appendChild(tags);
  card.appendChild(meta);
  card.appendChild(reasons);
  card.appendChild(actions);

  return card;
};

const renderMatches = (fullMatches, partialMatches) => {
  if (!matchResults) {
    return;
  }

  matchResults.innerHTML = "";

  if (fullMatchCount) {
    fullMatchCount.textContent = fullMatches.length;
  }
  if (partialMatchCount) {
    partialMatchCount.textContent = partialMatches.length;
  }

  if (fullMatches.length === 0 && partialMatches.length === 0) {
    const empty = document.createElement("p");
    empty.className = "note";
    empty.textContent = "No matches yet. Try adjusting your details.";
    matchResults.appendChild(empty);
    return;
  }

  if (fullMatches.length) {
    const label = document.createElement("p");
    label.className = "match-status";
    label.textContent = "Full matches";
    matchResults.appendChild(label);
    fullMatches.forEach((match) => matchResults.appendChild(buildMatchCard(match)));
  }

  if (partialMatches.length) {
    const label = document.createElement("p");
    label.className = "match-status";
    label.textContent = "Partial matches";
    matchResults.appendChild(label);
    partialMatches.forEach((match) =>
      matchResults.appendChild(buildMatchCard(match))
    );
  }
};

const updateMatches = () => {
  if (!matchResults || !funnelInputs.category) {
    return;
  }

  const selectedCategory = funnelInputs.category.value;
  const location = funnelInputs.location?.value || "";
  const details = funnelInputs.details?.value || "";
  const budgetRange = budgetRanges[funnelInputs.budget?.value];
  const timelineLimit = timelineTargets[funnelInputs.timeline?.value];
  const propertyType = funnelInputs.property?.value || "";

  const matches = proDirectory.map((pro) => {
    const categoryMatch = pro.categories.includes(selectedCategory);
    const locationMatch = matchesLocation(location, pro.serviceAreas);
    const budgetMatch = budgetRange
      ? pro.minBudget <= budgetRange.max && pro.maxBudget >= budgetRange.min
      : false;
    const budgetNearMatch =
      !budgetMatch && budgetRange
        ? pro.minBudget <= budgetRange.max * 1.2 &&
          pro.maxBudget >= budgetRange.min * 0.8
        : false;
    const timelineMatch =
      typeof timelineLimit === "number"
        ? pro.responseTimeHours <= timelineLimit
        : false;
    const propertyMatch = propertyType
      ? pro.propertyTypes.includes(propertyType)
      : false;
    const keywordMatch = matchesKeywords(details, pro.keywords);

    const { score, reasons } = buildMatchScore(pro, {
      categoryMatch,
      locationMatch,
      budgetMatch,
      budgetNearMatch,
      timelineMatch,
      propertyMatch,
      keywordMatch,
    });

    const maxScore = 115;
    const percent = Math.min(100, Math.round((score / maxScore) * 100));
    const isFull = categoryMatch && locationMatch && budgetMatch;

    return {
      pro,
      score,
      percent,
      isFull,
      reasons,
    };
  });

  const sortedMatches = matches
    .filter((match) => match.score >= 30)
    .sort((a, b) => b.score - a.score);

  const fullMatches = sortedMatches.filter((match) => match.isFull);
  const partialMatches = sortedMatches.filter((match) => !match.isFull);

  renderMatches(fullMatches, partialMatches);
};

Object.values(funnelInputs).forEach((field) => {
  if (!field) {
    return;
  }
  field.addEventListener("input", updateMatches);
  field.addEventListener("change", updateMatches);
});

if (funnelSubmit) {
  funnelSubmit.addEventListener("click", updateMatches);
}

updateMatches();

updateRole("pro");
resetLeadDemo();
