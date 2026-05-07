const API_BASE = "http://localhost:8000/api";
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
        
        const assignment = await resp.json();

        if (assignment.assignment_type === "pdf") {
            const fileResp = await fetch(`${API_BASE}/assignments/${id}/file`, {
                headers: { "Authorization": `Bearer ${token}` }
            });
            const blob = await fileResp.blob();
            const url = window.URL.createObjectURL(blob);
            
            container.innerHTML = `
                <h2 class="gradient-text">${assignment.title}</h2>
                <div class="desc">${assignment.description || "No description provided."}</div>
                <iframe src="${url}" width="100%" height="600px" style="margin-top:1rem; border: none; border-radius: var(--radius)"></iframe>
            `;
            return;
        }
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

// --- Study Planning Logic ---
const studySection = document.getElementById("study-section");
let currentCourseId = null;

async function fetchStudyDashboard() {
    try {
        const resp = await fetch(`${API_BASE}/course/all`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const courses = await resp.json();
        renderStudyCourses(courses);
    } catch (err) {
        console.error(err);
    }
}

function renderStudyCourses(courses) {
    const list = document.getElementById("study-list");
    if (!list) return;
    list.innerHTML = courses.map(c => `
        <div class="list-item" onclick="openStudyView('${c.id}')">
            <div class="item-info">
                <h4>${c.title}</h4>
                <p>Version ${c.version} | ${c.total_lectures} Lectures</p>
            </div>
            <div class="item-action">View Plan</div>
        </div>
    `).join("");
}

async function openStudyView(courseId) {
    currentCourseId = courseId;
    dashboardSection.classList.remove("active");
    studySection.classList.add("active");
    
    const dayPlan = document.getElementById("day-wise-plan");
    const startForm = document.getElementById("start-course-form");
    dayPlan.innerHTML = "<div class='skeleton'></div>";
    startForm.style.display = "none";

    try {
        const resp = await fetch(`${API_BASE}/study-plan/${courseId}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        
        if (resp.status === 404) {
            dayPlan.innerHTML = "<p>No study plan found. Please generate one to get started!</p>";
            startForm.style.display = "block";
            return;
        }

        const plan = await resp.json();
        const progressResp = await fetch(`${API_BASE}/progress/${courseId}`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        const progress = await progressResp.json();
        
        renderPlan(plan, progress);
    } catch (err) {
        console.error(err);
    }
}

function renderPlan(plan, progress) {
    document.getElementById("plan-course-title").innerText = `Study Plan (v${plan.course_version})`;
    const progressBar = document.getElementById("plan-progress");
    const progressText = document.getElementById("plan-progress-text");
    
    progressBar.style.width = `${progress.progress_percentage}%`;
    progressText.innerText = `${Math.round(progress.progress_percentage)}% Completed`;

    const dayPlan = document.getElementById("day-wise-plan");
    dayPlan.innerHTML = Object.entries(plan.plan).map(([day, lectureIds]) => `
        <div class="day-card">
            <h3>Day ${day.replace('day', '')}</h3>
            <div class="lecture-list">
                ${lectureIds.map(id => {
                    const isCompleted = progress.completed_lectures.includes(id);
                    return `
                        <div class="lecture-item ${isCompleted ? 'completed' : ''}">
                            <div class="lect-meta">
                                <h4>Lecture ID: ${id.substring(id.length - 4)}</h4>
                            </div>
                            ${!isCompleted ? `<button onclick="markComplete('${id}')" class="btn-complete">Mark Done</button>` : '<span>✅</span>'}
                        </div>
                    `;
                }).join("")}
            </div>
        </div>
    `).join("");
}

async function generatePlan() {
    const dailyMinutes = document.getElementById("daily-minutes").value;
    const schedule = {
        "monday": parseInt(document.getElementById("avail-mon").value),
        "tuesday": parseInt(document.getElementById("avail-tue").value),
        "wednesday": parseInt(document.getElementById("avail-wed").value),
        "thursday": parseInt(document.getElementById("avail-thu").value),
        "friday": parseInt(document.getElementById("avail-fri").value),
        "saturday": parseInt(document.getElementById("avail-sat").value),
        "sunday": parseInt(document.getElementById("avail-sun").value)
    };

    try {
        const resp = await fetch(`${API_BASE}/course/start`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                course_id: currentCourseId,
                daily_minutes: parseInt(dailyMinutes),
                weekly_schedule: schedule
            })
        });

        if (!resp.ok) throw new Error("Failed to generate plan");
        openStudyView(currentCourseId);
    } catch (err) {
        alert(err.message);
    }
}

async function markComplete(lectureId) {
    try {
        const resp = await fetch(`${API_BASE}/lecture/complete`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                course_id: currentCourseId,
                lecture_id: lectureId
            })
        });

        if (resp.ok) {
            openStudyView(currentCourseId);
        }
    } catch (err) {
        console.error(err);
    }
}

// Intercept showDashboard to fetch study data
const originalShowDashboard = showDashboard;
window.showDashboard = async function() {
    authSection.classList.remove("active");
    quizSection.classList.remove("active");
    assignmentSection.classList.remove("active");
    studySection.classList.remove("active");
    adminSection.classList.remove("active");
    dashboardSection.classList.add("active");
    
    fetchDashboardData();
    fetchStudyDashboard();
};

// --- Admin Logic ---
const adminSection = document.getElementById("admin-section");

function showAdmin() {
    authSection.classList.remove("active");
    dashboardSection.classList.remove("active");
    quizSection.classList.remove("active");
    assignmentSection.classList.remove("active");
    studySection.classList.remove("active");
    adminSection.classList.add("active");
}

document.getElementById("course-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("course-title").value;
    const description = document.getElementById("course-desc").value;

    try {
        const resp = await fetch(`${API_BASE}/course/create`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ title, description })
        });
        if (resp.ok) {
            const data = await resp.json();
            alert(`Course Created! ID: ${data.id}`);
            document.getElementById("course-form").reset();
        }
    } catch (err) {
        alert(err.message);
    }
});

document.getElementById("lecture-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const course_id = document.getElementById("lect-course-id").value;
    const title = document.getElementById("lect-title").value;
    const video_url = document.getElementById("lect-url").value;
    const duration = parseInt(document.getElementById("lect-duration").value);
    const order_index = parseInt(document.getElementById("lect-order").value);

    try {
        const resp = await fetch(`${API_BASE}/lecture/upload`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ course_id, title, video_url, duration, order_index })
        });
        if (resp.ok) {
            alert("Lecture Uploaded!");
            document.getElementById("lecture-form").reset();
        }
    } catch (err) {
        alert(err.message);
    }
});
