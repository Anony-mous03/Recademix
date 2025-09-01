  document.addEventListener('DOMContentLoaded', function() {
    const mobileToggle = document.getElementById('mobileToggle');
    const navLinks = document.getElementById('navLinks');
    const navOverlay = document.getElementById('navOverlay');
    
    // Toggle mobile menu
    mobileToggle.addEventListener('click', function() {
        const isActive = navLinks.classList.contains('active');
        
        if (isActive) {
            closeMobileMenu();
        } else {
            openMobileMenu();
        }
    });
    
    // Close menu when clicking overlay
    navOverlay.addEventListener('click', closeMobileMenu);
    
    // Close menu when clicking nav links
    navLinks.addEventListener('click', function(e) {
        if (e.target.tagName === 'A') {
            closeMobileMenu();
        }
    });
    
    // Close menu on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeMobileMenu();
        }
    });
    
    // Close menu on window resize if above mobile breakpoint
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobileMenu();
        }
    });
    
    function openMobileMenu() {
        mobileToggle.classList.add('active');
        navLinks.classList.add('active');
        navOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    function closeMobileMenu() {
        mobileToggle.classList.remove('active');
        navLinks.classList.remove('active');
        navOverlay.classList.remove('active');
        document.body.style.overflow = '';
    }
});