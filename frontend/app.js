const API_BASE = "http://localhost:8000";
let token = localStorage.getItem("token");
let user = null;

// --- DOM Elements ---
const authSection = document.getElementById("auth-section");
const dashboardSection = document.getElementById("dashboard-section");
const quizSection = document.getElementById("quiz-section");
const assignmentSection = document.getElementById("assignment-section");

// --- Initialization ---
if (token) {
    showDashboard();
}

// --- Auth Functions ---
async function login(e) {
    e.preventDefault();
    const email = document.getElementById("login-email").value;
    const password = document.getElementById("login-password").value;

    try {
        const formData = new FormData();
        formData.append("username", email);
        formData.append("password", password);

        const resp = await fetch(`${API_BASE}/auth/login`, {
            method: "POST",
            body: formData
        });

        if (!resp.ok) throw new Error("Invalid credentials");
        
        const data = await resp.json();
        token = data.access_token;
        localStorage.setItem("token", token);
        showDashboard();
    } catch (err) {
        alert(err.message);
    }
}

document.getElementById("login-form").addEventListener("submit", login);

function logout() {
    localStorage.removeItem("token");
    token = null;
    authSection.classList.add("active");
    dashboardSection.classList.remove("active");
}

// --- Navigation ---
async function showDashboard() {
    authSection.classList.remove("active");
    quizSection.classList.remove("active");
    assignmentSection.classList.remove("active");
    dashboardSection.classList.add("active");
    
    fetchDashboardData();
}

async function fetchDashboardData() {
    try {
        const resp = await fetch(`${API_BASE}/check-yourself`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (resp.status === 401) return logout();
        const data = await resp.json();
        
        renderAssignments(data.assignments);
        renderQuizzes(data.quizzes);
    } catch (err) {
        console.error(err);
    }
}

function renderAssignments(assignments) {
    const list = document.getElementById("assignments-list");
    list.innerHTML = assignments.map(a => `
        <div class="list-item" onclick="openAssignment('${a.id}')">
            <div class="item-info">
                <h4>${a.title}</h4>
                <p>${a.assignment_type.toUpperCase()} Practice</p>
            </div>
            <div class="item-action">→</div>
        </div>
    `).join("");
}

function renderQuizzes(quizzes) {
    const list = document.getElementById("quizzes-list");
    list.innerHTML = quizzes.map(q => `
        <div class="list-item" onclick="openQuiz('${q.id}')">
            <div class="item-info">
                <h4>${q.title}</h4>
                <p>${q.question_count} Questions</p>
            </div>
            <div class="item-action">→</div>
        </div>
    `).join("");
}

// --- Quiz Logic ---
async function openQuiz(id) {
    dashboardSection.classList.remove("active");
    quizSection.classList.add("active");
    const container = document.getElementById("quiz-container");
    container.innerHTML = "<div class='skeleton'></div>";

    try {
        const resp = await fetch(`${API_BASE}/quiz/${id}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const quiz = await resp.json();
        
        container.innerHTML = `
            <h2 class="gradient-text">${quiz.title}</h2>
            <div id="quiz-questions">
                ${quiz.questions.map((q, idx) => `
                    <div class="question-block" data-qid="${q.id}">
                        <h3>${idx + 1}. ${q.question}</h3>
                        <div class="options-grid">
                            <button class="option-btn" onclick="selectOption(this, 'A')">${q.option_a}</button>
                            <button class="option-btn" onclick="selectOption(this, 'B')">${q.option_b}</button>
                            <button class="option-btn" onclick="selectOption(this, 'C')">${q.option_c}</button>
                            <button class="option-btn" onclick="selectOption(this, 'D')">${q.option_d}</button>
                        </div>
                    </div>
                `).join("")}
            </div>
            <button onclick="submitQuiz('${id}')" class="btn-primary">Submit Answers</button>
        `;
    } catch (err) {
        console.error(err);
    }
}

function selectOption(btn, val) {
    const parent = btn.closest(".options-grid");
    parent.querySelectorAll(".option-btn").forEach(b => b.classList.remove("selected"));
    btn.classList.add("selected");
    btn.dataset.value = val;
}

async function submitQuiz(id) {
    const questions = document.querySelectorAll(".question-block");
    const answers = [];
    questions.forEach(q => {
        const selected = q.querySelector(".option-btn.selected");
        if (selected) {
            answers.push({
                question_id: q.dataset.qid,
                selected_answer: selected.dataset.value
            });
        }
    });

    const resp = await fetch(`${API_BASE}/quiz/${id}/submit`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ answers })
    });

    const result = await resp.json();
    alert(`Quiz Submitted! Score: ${result.score}/${result.total} (${result.percentage}%)`);
    showDashboard();
}

// --- Assignment Logic ---
async function openAssignment(id) {
    dashboardSection.classList.remove("active");
    assignmentSection.classList.add("active");
    const container = document.getElementById("assignment-container");
    container.innerHTML = "<div class='skeleton'></div>";

    try {
        const resp = await fetch(`${API_BASE}/assignments/${id}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        // Handle PDF via direct blob or redirect
        if (resp.headers.get("content-type") === "application/pdf") {
            const blob = await resp.blob();
            const url = window.URL.createObjectURL(blob);
            container.innerHTML = `
                <h2>PDF Assignment</h2>
                <iframe src="${url}" width="100%" height="600px"></iframe>
            `;
            return;
        }

        const assignment = await resp.json();
        container.innerHTML = `
            <h2 class="gradient-text">${assignment.title}</h2>
            <div class="desc">${assignment.description || "No description provided."}</div>
            <p style="margin-top:1rem; color:var(--text-muted)">Target Function: <code>${assignment.function_name}</code></p>
            <textarea id="code-input" class="code-editor" placeholder="Write your solution here...">${assignment.starter_code || ""}</textarea>
            <button onclick="submitCode('${id}')" class="btn-primary">Run & Submit</button>
            <div id="code-result" style="margin-top:1rem"></div>
        `;
    } catch (err) {
        console.error(err);
    }
}

async function submitCode(id) {
    const code = document.getElementById("code-input").value;
    const resultDiv = document.getElementById("code-result");
    resultDiv.innerHTML = "Submitting...";

    const resp = await fetch(`${API_BASE}/coding-assignments/submit`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
            assignment_id: id,
            code: code,
            language: "python"
        })
    });

    const sub = await resp.json();
    pollSubmission(sub.id);
}

async function pollSubmission(subId) {
    const resultDiv = document.getElementById("code-result");
    const interval = setInterval(async () => {
        const resp = await fetch(`${API_BASE}/coding-assignments/submissions/${subId}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const res = await resp.json();
        resultDiv.innerHTML = `Status: <span class="badge">${res.status}</span>`;
        
        if (res.status !== "pending" && res.status !== "running") {
            clearInterval(interval);
            resultDiv.innerHTML = `
                <div class="glass-card" style="margin-top:1rem">
                    <h3>Result: ${res.status}</h3>
                    <p>Score: ${res.score}% (${res.passed_cases}/${res.total_cases})</p>
                    ${res.error_message ? `<p style="color:#ef4444">Error: ${res.error_message}</p>` : ""}
                </div>
            `;
        }
    }, 2000);
}
