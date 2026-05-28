document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.getElementById("applicationSearch");
    const table = document.getElementById("applicationsTable");
    if (searchInput && table) {
        searchInput.addEventListener("input", function () {
            const query = searchInput.value.toLowerCase();
            table.querySelectorAll("tbody tr").forEach(row => {
                row.style.display = row.textContent.toLowerCase().includes(query) ? "" : "none";
            });
        });
    }

    // Run only on pages that contain the loan multi-step form
    const form = document.getElementById("loanApplicationForm");
    if (!form) return;

    // Step containers
    const step1 = document.getElementById("step-1");
    const step2 = document.getElementById("step-2");
    const step3 = document.getElementById("step-3");

    // Progress bar items
    const progress1 = document.getElementById("progress-1");
    const progress2 = document.getElementById("progress-2");
    const progress3 = document.getElementById("progress-3");

    // Buttons
    const nextStep1 = document.getElementById("next-step-1");
    const backStep2 = document.getElementById("back-step-2");
    const nextStep2 = document.getElementById("next-step-2");
    const backStep3 = document.getElementById("back-step-3");

    function showStep(stepNumber) {
        // Hide all steps
        step1.classList.remove("active-step");
        step2.classList.remove("active-step");
        step3.classList.remove("active-step");

        // Reset progress state
        [progress1, progress2, progress3].forEach(step => {
            step.classList.remove("active", "completed");
        });

        if (stepNumber === 1) {
            step1.classList.add("active-step");
            progress1.classList.add("active");
        }

        if (stepNumber === 2) {
            step2.classList.add("active-step");
            progress1.classList.add("completed");
            progress2.classList.add("active");
        }

        if (stepNumber === 3) {
            step3.classList.add("active-step");
            progress1.classList.add("completed");
            progress2.classList.add("completed");
            progress3.classList.add("active");
        }

        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    function validateStep(stepElement) {
        const fields = stepElement.querySelectorAll("input, select, textarea");

        for (let field of fields) {
            if (!field.checkValidity()) {
                field.reportValidity();
                field.focus();
                return false;
            }
        }

        return true;
    }

    function getDisplayValue(fieldName) {
        const field = form.querySelector(`[name="${fieldName}"]`);
        if (!field) return "-";

        if (field.tagName === "SELECT") {
            return field.options[field.selectedIndex]?.text || "-";
        }

        return field.value.trim() || "-";
    }

    function fillReview() {
        const fields = [
            "customer_name",
            "customer_email",
            "person_age",
            "person_gender",
            "person_education",
            "person_income",
            "person_emp_exp",
            "person_home_ownership",
            "credit_score",
            "credit_history_length",
            "previous_loan_defaults_on_file",
            "loan_amnt",
            "loan_int_rate",
            "loan_intent"
        ];

        fields.forEach(fieldName => {
            const reviewTarget = document.getElementById(`review-${fieldName}`);
            if (reviewTarget) {
                reviewTarget.textContent = getDisplayValue(fieldName);
            }
        });
    }

    function updateCompletion() {
        const fields = Array.from(form.querySelectorAll("input, select"));
        const requiredFields = fields.filter(field => field.required);
        const completed = requiredFields.filter(field => field.value && field.value.trim() !== "").length;
        const percent = requiredFields.length ? Math.round((completed / requiredFields.length) * 100) : 0;
        const percentTarget = document.getElementById("completionPercent");
        const barTarget = document.getElementById("completionBar");
        if (percentTarget) percentTarget.textContent = `${percent}%`;
        if (barTarget) barTarget.style.width = `${percent}%`;
    }

    form.addEventListener("input", updateCompletion);
    form.addEventListener("change", updateCompletion);

    if (nextStep1) {
        nextStep1.addEventListener("click", function () {
            if (validateStep(step1)) {
                showStep(2);
            }
        });
    }

    if (backStep2) {
        backStep2.addEventListener("click", function () {
            showStep(1);
        });
    }

    if (nextStep2) {
        nextStep2.addEventListener("click", function () {
            if (validateStep(step2)) {
                fillReview();
                showStep(3);
            }
        });
    }

    if (backStep3) {
        backStep3.addEventListener("click", function () {
            showStep(2);
        });
    }

    // Start on Step 1
    showStep(1);
    updateCompletion();
});
