
//  Configuration

const API_BASE = "http://localhost:8000";


// Utility
function $(id) {
  return document.getElementById(id);
}



//  Rendering Helpers

function renderEmptyState(message = "No recommendations yet.") {
  const box = $("results-box");
  box.innerHTML = `
    <div class="empty-state">
      ${message}
    </div>
  `;
}

function renderResults(query, recs) {
  const box = $("results-box");
  const meta = $("results-meta");

  if (!recs || recs.length === 0) {
    meta.textContent = "0 assessments";
    renderEmptyState("No assessments returned for this query.");
    return;
  }

  meta.textContent = `${recs.length} assessments`;

  const rowsHtml = recs
    .map((r, idx) => {
      const name = r.name || "(Unnamed assessment)";
      const url = r.url || "#";
      const duration =
        typeof r.duration === "number" && r.duration > 0
          ? `${r.duration} min`
          : "N/A";
      const remote = (r.remote_support || "Unknown").toString();
      const adaptive = (r.adaptive_support || "Unknown").toString();
      const testTypes = Array.isArray(r.test_type) ? r.test_type : [];

      const remoteClass =
        remote.toLowerCase() === "yes"
          ? "pill pill-yes"
          : remote.toLowerCase() === "no"
          ? "pill pill-no"
          : "pill pill-unknown";

      const adaptiveClass =
        adaptive.toLowerCase() === "yes"
          ? "pill pill-yes"
          : adaptive.toLowerCase() === "no"
          ? "pill pill-no"
          : "pill pill-unknown";

      const tagsHtml =
        testTypes.length > 0
          ? testTypes.map((t) => `<span class="tag">${t}</span>`).join(" ")
          : '<span class="tag">Unspecified</span>';

      return `
        <tr>
          <td>${idx + 1}</td>
          <td>
            <div>
              <a href="${url}" class="url-link" target="_blank" rel="noopener noreferrer">
                ${name}
              </a>
            </div>
            <div class="duration-badge">${duration}</div>
          </td>
          <td><span class="${remoteClass}">Remote: ${remote}</span></td>
          <td><span class="${adaptiveClass}">Adaptive: ${adaptive}</span></td>
          <td><div class="tag-list">${tagsHtml}</div></td>
        </tr>
      `;
    })
    .join("");

  box.innerHTML = `
    <table>
      <thead>
        <tr>
          <th>#</th>
          <th>Assessment</th>
          <th>Remote support</th>
          <th>Adaptive</th>
          <th>Test type</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHtml}
      </tbody>
    </table>
  `;
}



//  Backend Call

async function callRecommend(query, k, preferRemote, preferAdaptive) {
  const payload = {
    query,
    k,
    prefer_remote: preferRemote,
    prefer_adaptive: preferAdaptive,
  };

  const resp = await fetch(`${API_BASE}/recommend`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(
      `HTTP ${resp.status} from /recommend: ${text.slice(0, 200)}`
    );
  }

  const data = await resp.json();
  return data.recommended_assessments || [];
}



//  UI Helpers

function setLoading(isLoading) {
  const btn = $("submit-btn");
  const icon = $("btn-icon");
  const text = $("btn-text");

  btn.disabled = isLoading;
  if (isLoading) {
    icon.textContent = "⏳";
    text.textContent = "Finding assessments...";
  } else {
    icon.textContent = "⚙️";
    text.textContent = "Get recommendations";
  }
}

function setError(message) {
  const el = $("error-msg");
  if (!message) {
    el.style.display = "none";
    el.textContent = "";
  } else {
    el.style.display = "block";
    el.textContent = message;
  }
}



//  Init

function init() {
  console.log("Frontend init() started.");

  const form = $("query-form");
  const queryInput = $("query-input");
  const kInput = $("k-input");
  const remoteFilter = $("remote-filter");
  const adaptiveFilter = $("adaptive-filter");

  if (!form) {
    console.error("Form not found. Check HTML IDs.");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    setError("");

    const rawQuery = (queryInput.value || "").trim();
    if (!rawQuery) {
      setError("Please enter a hiring requirement first.");
      renderEmptyState("Waiting for a query...");
      return;
    }

    // k (max recommendations)
    let k = parseInt(kInput.value, 10);
    if (Number.isNaN(k) || k <= 0) k = 10;
    if (k > 10) k = 10;

    const preferRemote = !!remoteFilter.checked;
    const preferAdaptive = !!adaptiveFilter.checked;

    setLoading(true);
    $("results-meta").textContent = "Request in flight...";

    try {
      const recs = await callRecommend(
        rawQuery,
        k,
        preferRemote,
        preferAdaptive
      );
      renderResults(rawQuery, recs.slice(0, k));
      setError("");
    } catch (err) {
      console.error(err);
      setError("Failed to fetch recommendations. Check backend & retry.");
      renderEmptyState("Error calling backend.");
    } finally {
      setLoading(false);
    }
  });
}


// =======================
//  Start immediately
// =======================
init();
