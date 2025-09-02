//quiz.js
document.addEventListener('DOMContentLoaded', function() {
    // Add visual feedback when selecting options
    const options = document.querySelectorAll('.option-block');
    options.forEach(option => {
        const radio = option.querySelector('input[type="radio"]');
        if (radio) {
            option.addEventListener('click', function() {
                // Remove active class from all options
                options.forEach(opt => opt.classList.remove('active'));
                // Add active class to selected option
                if (!radio.disabled) {
                    option.classList.add('active');
                    radio.checked = true;
                }
            });
        }
    });
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

function handleFeedback(feedback) {
    // Clear previous highlights
    document.querySelectorAll('.option').forEach(opt => {
        opt.classList.remove('wrong-option', 'correct-option');
    });

    // Highlight wrong option if selected and wrong
    if (feedback.selected_option_id && feedback.type === "error") {
        const wrongOpt = document.querySelector(`input[value="${feedback.selected_option_id}"]`)?.closest('.option');
        if (wrongOpt) wrongOpt.classList.add('wrong-option');
    }

    // Highlight correct option if revealed
    if (feedback.correct_option_id) {
        const correctOpt = document.querySelector(`input[value="${feedback.correct_option_id}"]`)?.closest('.option');
        if (correctOpt) correctOpt.classList.add('correct-option');
    }

    // Show hint
    if (feedback.show_hint) {
        document.getElementById("hint-box").style.display = "block";
        document.getElementById("hint-box").innerText = feedback.message;
    } else {
        document.getElementById("hint-box").style.display = "none";
    }

    // Show explanation
    if (feedback.show_explanation) {
        document.getElementById("explanation-box").style.display = "block";
        document.getElementById("explanation-box").innerText = feedback.explanation || "";
    } else {
        document.getElementById("explanation-box").style.display = "none";
    }
}


