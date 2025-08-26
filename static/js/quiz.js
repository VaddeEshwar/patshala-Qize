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