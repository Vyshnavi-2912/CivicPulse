/* ==========================================================================
   CivicPulse Main UI Javascript Module
   ========================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const mobileToggle = document.getElementById('mobileToggle');
    const navMenu = document.getElementById('navMenu');

    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function() {
            navMenu.classList.toggle('show');
        });
    }

    // Auto dismiss alert notifications after 5s
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(function() {
                if (alert.parentNode) alert.parentNode.removeChild(alert);
            }, 500);
        }, 5000);
    });

    // Upvote Button Handler
    const upvoteBtns = document.querySelectorAll('.btn-upvote');
    upvoteBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            const reportId = this.getAttribute('data-report-id');
            const countSpan = this.querySelector('.upvote-count');
            
            fetch(`/api/report/${reportId}/upvote`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success && countSpan) {
                    countSpan.textContent = data.new_upvotes;
                    this.style.transform = 'scale(1.1)';
                    setTimeout(() => { this.style.transform = 'scale(1)'; }, 200);
                }
            })
            .catch(err => console.error("Error upvoting report:", err));
        });
    });
});
