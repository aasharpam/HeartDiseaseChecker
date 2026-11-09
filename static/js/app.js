const form = document.getElementById("heartForm");
const ageInput = document.getElementById("age");
const maxHrInput = document.getElementById("maxHr");
const maxHrHint = document.getElementById("maxHrHint");
const result = document.getElementById("result");
const resultTitle = document.getElementById("resultTitle");
const resultCopy = document.getElementById("resultCopy");
const meterFill = document.getElementById("meterFill");
const submitBtn = document.getElementById("submitBtn");
const themeRange = document.getElementById("themeRange");
const root = document.documentElement;

const LIMITS = {
  Age: { min: 18, max: 100, message: "Age must be between 18 and 100." },
  RestingBP: { min: 80, max: 200, message: "Resting blood pressure must be 80–200 mmHg." },
  Cholesterol: { min: 50, max: 600, message: "Cholesterol must be 50–600 mg/dL." },
  Oldpeak: { min: -3, max: 7, message: "Oldpeak must be between -3.0 and 7.0." },
  MaxHR: { min: 60, max: 220, message: "Max heart rate must be 60–220 bpm." },
};

function setTheme(isDark) {
  root.dataset.theme = isDark ? "dark" : "light";
  themeRange.value = isDark ? "1" : "0";
  localStorage.setItem("pulse-theme", isDark ? "dark" : "light");
  document.querySelector('meta[name="theme-color"]').setAttribute("content", isDark ? "#0e1116" : "#9b2335");
}

const saved = localStorage.getItem("pulse-theme");
const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
setTheme(saved ? saved === "dark" : prefersDark);

themeRange.addEventListener("input", () => setTheme(themeRange.value === "1"));

function clearErrors() {
  document.querySelectorAll(".error").forEach((el) => {
    el.textContent = "";
  });
}

function showError(name, message) {
  const el = document.querySelector(`[data-error-for="${name}"]`);
  if (el) el.textContent = message;
}

function updateMaxHr() {
  const age = Number(ageInput.value);
  if (!age || age < 18 || age > 100) {
    maxHrHint.textContent = "Enter age to auto-fill 220 − age";
    return;
  }
  const formula = 220 - age;
  maxHrInput.value = formula;
  maxHrHint.textContent = `Auto-filled as 220 − ${age} = ${formula} bpm (you may adjust ±40)`;
}

ageInput.addEventListener("input", updateMaxHr);

function validate() {
  clearErrors();
  const data = Object.fromEntries(new FormData(form).entries());
  let ok = true;

  if (!data.Age) {
    showError("Age", "Age is required.");
    ok = false;
  } else if (Number(data.Age) < LIMITS.Age.min || Number(data.Age) > LIMITS.Age.max) {
    showError("Age", LIMITS.Age.message);
    ok = false;
  }

  ["Sex", "ChestPainType", "FastingBS", "RestingECG", "ExerciseAngina", "ST_Slope"].forEach((key) => {
    if (!data[key]) {
      showError(key, "This field is required.");
      ok = false;
    }
  });

  ["RestingBP", "Cholesterol", "Oldpeak", "MaxHR"].forEach((key) => {
    if (data[key] === undefined || data[key] === "") {
      showError(key, "This field is required.");
      ok = false;
      return;
    }
    const value = Number(data[key]);
    if (Number.isNaN(value) || value < LIMITS[key].min || value > LIMITS[key].max) {
      showError(key, LIMITS[key].message);
      ok = false;
    }
  });

  if (data.Age && data.MaxHR) {
    const expected = 220 - Number(data.Age);
    if (Math.abs(Number(data.MaxHR) - expected) > 40) {
      showError("MaxHR", `Keep max heart rate near 220 − age (${expected} bpm).`);
      ok = false;
    }
  }

  return { ok, data };
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const { ok, data } = validate();
  if (!ok) {
    result.hidden = true;
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = "Screening…";
  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...data,
        Age: Number(data.Age),
        RestingBP: Number(data.RestingBP),
        Cholesterol: Number(data.Cholesterol),
        FastingBS: Number(data.FastingBS),
        MaxHR: Number(data.MaxHR),
        Oldpeak: Number(data.Oldpeak),
      }),
    });
    const payload = await response.json();
    if (!response.ok) {
      result.hidden = false;
      result.className = "result risk";
      resultTitle.textContent = "Check the form";
      resultCopy.textContent = payload.error || "Could not run the screening.";
      meterFill.style.width = "0%";
      return;
    }
    const risk = payload.prediction === 1;
    result.hidden = false;
    result.className = `result ${risk ? "risk" : "clear"}`;
    resultTitle.textContent = risk ? "Heart disease signal detected" : "No disease signal";
    resultCopy.textContent = `Estimated probability: ${payload.probability}%. Max HR formula used nearby ${payload.max_hr_formula} bpm. This is an educational model result, not a clinical diagnosis.`;
    meterFill.style.width = `${payload.probability}%`;
    result.scrollIntoView({ behavior: "smooth", block: "nearest" });
  } catch {
    result.hidden = false;
    result.className = "result risk";
    resultTitle.textContent = "Connection issue";
    resultCopy.textContent = "Could not reach the screening service. Try again.";
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Run screening";
  }
});

form.addEventListener("reset", () => {
  clearErrors();
  result.hidden = true;
  maxHrHint.textContent = "Enter age to auto-fill 220 − age";
});

const aboutBtn = document.getElementById("aboutBtn");
const aboutModal = document.getElementById("aboutModal");

function openAbout() {
  aboutModal.hidden = false;
  document.body.style.overflow = "hidden";
  const closeBtn = aboutModal.querySelector(".about-close");
  if (closeBtn) closeBtn.focus();
}

function closeAbout() {
  aboutModal.hidden = true;
  document.body.style.overflow = "";
  aboutBtn.focus();
}

aboutBtn.addEventListener("click", openAbout);
aboutModal.addEventListener("click", (event) => {
  if (event.target.closest("[data-about-close]")) {
    closeAbout();
  }
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !aboutModal.hidden) {
    closeAbout();
  }
});
