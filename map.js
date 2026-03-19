// ======== CONSTANTS ========
const CATEGORY_COLORS = {
  Artifact: "#ffbd59",
  Ruins: "#ff8652",
  Burial: "#c65dbb",
  Fossil: "#44bf6b",
  Shipwreck: "#527dd9",
};

const CATEGORY_SYMBOLS = {
  Artifact: "trophy",
  Ruins: "monument",
  Burial: "skull",
  Fossil: "dragon",
  Shipwreck: "sailboat",
};

let markers = [];
let articles = [];

let minStart = new Date();
let defaultStart = new Date();
let defaultEnd = new Date();
defaultStart.setDate(defaultEnd.getDate() - 7);
minStart.setDate(defaultEnd.getDate() - 28);
let selectedStart = defaultStart;
let selectedEnd = defaultEnd;

const isMobile = window.matchMedia("(max-width: 768px)").matches;

const API_URL = "/api/news";

// ======== MAP ========
const map = L.map("map", {
  maxBounds: [
    [-120, -180],
    [120, 240],
  ],
  maxBoundsViscosity: 1.0,
}).setView([25, 45], 3);

const tiles = L.tileLayer(
  "https://tile.jawg.io/28273ba0-bb64-49cc-ba1d-04db60b66173/{z}/{x}/{y}{r}.png?access-token=b5G5ZABuZXaR61R9blXMCBO4gMguFP6TU5KJWul4A1VMCX5PtzHZ43LL7mXd0qZP",
  { minZoom: 3 },
);
tiles.addTo(map);

map.attributionControl.addAttribution(
  `<a href="https://newsapi.org/" target="_blank">© NewsAPI</a> <a href="https://www.jawg.io?utm_medium=map&utm_source=attribution" target="_blank">© Jawg</a> <a href="https://www.mapbox.com/about/maps">© Mapbox</a> <a href="http://www.openstreetmap.org/copyright">© OpenStreetMap</a>`,
);

// https://newsapi.org/
// ======== DATE ========
const dateDisplay = document.getElementById("dateDisplay");
const dateCard = document.getElementById("dateCard");

function formatDate(date) {
  return `${date.getMonth() + 1}/${date.getDate()}`;
}

const fp = flatpickr("#dateRange", {
  mode: "range",
  dateFormat: "Y-m-d",
  defaultDate: [defaultStart, defaultEnd],
  minDate: minStart,
  maxDate: defaultEnd,
  monthSelectorType: "static",

  onReady: function (selectedDates) {
    if (selectedDates.length === 2) {
      dateDisplay.textContent = `${formatDate(selectedDates[0])}-${formatDate(selectedDates[1])}`;
    }
  },

  onChange: function (selectedDates) {
    if (selectedDates.length === 2) {
      dateDisplay.textContent = `${formatDate(selectedDates[0])}-${formatDate(selectedDates[1])}`;
      selectedStart = selectedDates[0];
      selectedEnd = selectedDates[1];
      loadNews();
    }
  },
});

dateCard.addEventListener("click", () => fp.open());

// ======== LEGEND ========
const legend = L.control({ position: "topright" });

legend.onAdd = function (map) {
  const div = L.DomUtil.create("div");
  div.id = "legend";
  div.innerHTML = `
        <div class="legend-title">FILTERS</div>
        <label class="checklist-item">
            <input type="checkbox" class="category-filter" value="Artifact" checked>
            <div class="checkmark"></div>
            <div class="checklist-text">Artifacts</div>
        </label>
        <label class="checklist-item">
            <input type="checkbox" class="category-filter" value="Ruins" checked>
            <div class="checkmark"></div>
            <div class="checklist-text">Ruins</div>
        </label>
        <label class="checklist-item">
            <input type="checkbox" class="category-filter" value="Burial" checked>
            <div class="checkmark"></div>
            <div class="checklist-text">Burials</div>
        </label>
        <label class="checklist-item">
            <input type="checkbox" class="category-filter" value="Fossil" checked>
            <div class="checkmark"></div>
            <div class="checklist-text">Fossils</div>
        </label>
        <label class="checklist-item">
            <input type="checkbox" class="category-filter" value="Shipwreck" checked>
            <div class="checkmark"></div>
            <div class="checklist-text">Shipwrecks</div>
        </label>
        <div class="legend-title">COUNTRY</div>
        <div class="legend-text">Coming soon!</div>
    `;

  L.DomEvent.disableClickPropagation(div);
  L.DomEvent.disableScrollPropagation(div);

  return div;
};

legend.addTo(map);

// ======== MARKERS ========
const markerCluster = L.markerClusterGroup({
  maxClusterRadius: 1,
  spiderLegPolylineOptions: { weight: 0 },
  iconCreateFunction: function (cluster) {
    return L.divIcon({
      html: `<div class="marker-group"></div>`,
      className: "",
      iconSize: L.point(30, 30),
    });
  },
}).addTo(map);

function createPopup(article) {
  const color = CATEGORY_COLORS[article.category];

  const category = article.category.toUpperCase();
  const title = article.title.toUpperCase();
  const description = article.description;
  const source = article.source.name;
  const url = article.url;

  return `
    <div class="article-popup" style="--accent-color: ${color};">
      <div class="category-pill" style="--accent-color: ${color};">${category}</div>
      <div class="title">${title}</div>
      <div class="description">${description || ""}</div>
      <button class="read-more" type="button" onclick="window.open('${url}', '_blank', 'noopener')">READ MORE</button>
      <div class="source">Source: ${source || ""}</div>
    </div>
  `;
}

function clearMarkers() {
  markerCluster.clearLayers();
  markers = [];
}

function addMarker(article) {
  const color = CATEGORY_COLORS[article.category];
  const symbol = CATEGORY_SYMBOLS[article.category];

  const icon = L.divIcon({
    className: "custom-marker",
    html: `
      <div class="marker-icon" style="color: ${color};">
        <i class="fa-solid fa-${symbol}"></i>
      </div>
    `,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
    popupAnchor: [0, -12],
  });

  const marker = L.marker([article.latitude, article.longitude], {
    icon,
  });
  marker.bindPopup(createPopup(article));

  markerCluster.addLayer(marker);
  markers.push(marker);
}

function renderMarkers(articles) {
  clearMarkers();
  const categories = document.querySelectorAll(".category-filter:checked");
  const filtered = Array.from(categories).map((category) => category.value);

  const filteredArticles = articles.filter((article) =>
    filtered.includes(article.category),
  );

  filteredArticles.forEach((article) => addMarker(article));
}

// ======== BACKEND ========
async function loadNews() {
  try {
    const params = new URLSearchParams({
      from: selectedStart.toISOString().split("T")[0],
      to: selectedEnd.toISOString().split("T")[0],
    });
    const response = await fetch(`${API_URL}?${params}`);
    const data = await response.json();

    articles = data.articles || [];

    renderMarkers(articles);
  } catch (error) {
    console.error("Error loading news:", error);
  }
}

if (!isMobile) {
  loadNews();
}

document.addEventListener("change", (event) => {
  if (event.target.classList.contains("category-filter")) {
    renderMarkers(articles);
  }
});
