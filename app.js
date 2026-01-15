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

updateRole("pro");
resetLeadDemo();
