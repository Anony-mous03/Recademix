function dismissAlert(button) {
    const alert = button.closest('.alert');
    alert.classList.add('dismissing');
    
    setTimeout(() => {
        if (alert && alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 300);
}

function initAutoDissmiss() {
    const alerts = document.querySelectorAll('.alert[data-auto-dismiss]');
    
    alerts.forEach(alert => {
        const duration = parseInt(alert.dataset.autoDismiss) || 10000;
        const progressBar = alert.querySelector('.alert-progress');
        
        // Start progress bar animation
        if (progressBar) {
            progressBar.style.animation = `progressBar ${duration}ms linear forwards`;
        }
        
        // Auto dismiss after duration
        const timeoutId = setTimeout(() => {
            if (alert && alert.parentNode) {
                dismissAlert(alert.querySelector('.alert-close'));
            }
        }, duration);
        
        // Clear timeout if manually dismissed
        alert.addEventListener('click', (e) => {
            if (e.target.closest('.alert-close')) {
                clearTimeout(timeoutId);
            }
        });
        
        // Pause auto-dismiss on hover
        alert.addEventListener('mouseenter', () => {
            if (progressBar) {
                progressBar.style.animationPlayState = 'paused';
            }
            clearTimeout(timeoutId);
        });
        
        // Resume auto-dismiss on mouse leave
        alert.addEventListener('mouseleave', () => {
            if (progressBar) {
                progressBar.style.animationPlayState = 'running';
            }
            const remainingTime = duration * (1 - (parseFloat(getComputedStyle(progressBar).transform.split(',')[0].split('(')[1]) || 0));
            setTimeout(() => {
                if (alert && alert.parentNode) {
                    dismissAlert(alert.querySelector('.alert-close'));
                }
            }, remainingTime);
        });
    });
}
// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initAutoDissmiss);