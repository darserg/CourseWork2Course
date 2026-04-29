const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const codeInput = document.getElementById("code");
const statusBox = document.getElementById("status");

const registerBtn = document.getElementById("registerBtn");
const loginBtn = document.getElementById("loginBtn");
const verifyBtn = document.getElementById("verifyBtn");

function showStatus(message, isError = false) {
  statusBox.style.border = `1px solid ${isError ? "#dc2626" : "#16a34a"}`;
  statusBox.textContent = message;
}

async function callApi(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return response.json();
}

registerBtn.addEventListener("click", async () => {
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (!email || !password) {
    showStatus("Введите email и пароль", true);
    return;
  }

  const result = await callApi("/api/register", { email, password });
  if (result.success) {
    window.location.href = "/success.html";
  } else {
    showStatus(result.message, true);
  }
});

loginBtn.addEventListener("click", async () => {
  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (!email || !password) {
    showStatus("Введите email и пароль", true);
    return;
  }

  const result = await callApi("/api/login", { email, password });
  if (!result.success) {
    showStatus(result.message, true);
    return;
  }

  showStatus(result.message);
});

verifyBtn.addEventListener("click", async () => {
  const email = emailInput.value.trim();
  const code = codeInput.value.trim();

  if (!email || !code) {
    showStatus("Введите email и код подтверждения", true);
    return;
  }

  const result = await callApi("/api/verify", { email, code });
  showStatus(result.message, !result.success);
});
