// Custom JavaScript for Photo Studio website

// Portfolio filtering functionality
document.addEventListener('DOMContentLoaded', function() {
    // Portfolio filtering
    const filterButtons = document.querySelectorAll('[data-category]');
    const portfolioItems = document.querySelectorAll('.portfolio-item');

    if (filterButtons.length > 0 && portfolioItems.length > 0) {
        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                filterButtons.forEach(btn => btn.classList.remove('active'));
                // Add active class to clicked button
                this.classList.add('active');

                const categoryId = parseInt(this.getAttribute('data-category'));

                portfolioItems.forEach(item => {
                    const itemCategoryId = parseInt(item.getAttribute('data-category'));
                    
                    if (categoryId === 0 || itemCategoryId === categoryId) {
                        item.style.display = 'block';
                        // Trigger animation
                        setTimeout(() => {
                            item.style.opacity = '1';
                            item.style.transform = 'translateY(0)';
                        }, 10);
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }

    // Initialize portfolio items with hidden state for animation
    portfolioItems.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        item.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
    });

    // Lightbox functionality for gallery
    const lightboxTriggers = document.querySelectorAll('[data-bs-toggle="modal"]');
    lightboxTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const imageSrc = this.getAttribute('data-image');
            const title = this.getAttribute('data-title');
            
            if (imageSrc) {
                document.getElementById('modalImage').src = imageSrc;
            }
            
            if (title) {
                document.getElementById('imageModalTitle').textContent = title;
            }
        });
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 70,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            // Add loading state to submit buttons
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Обработка...';
                submitBtn.disabled = true;
                
                // Re-enable button after form submission
                setTimeout(() => {
                    if (submitBtn) {
                        submitBtn.disabled = false;
                    }
                }, 3000);
            }
        });
    });

    // Intersection Observer for animations when elements come into view
    if ('IntersectionObserver' in window) {
        const observerOptions = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1
        };

        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                    observer.unobserve(entry.target);
                }
            });
        }, observerOptions);

        // Observe cards and other elements
        document.querySelectorAll('.card, .feature-box').forEach(el => {
            el.classList.add('animate__animated');
            observer.observe(el);
        });
    }
});

// Utility functions
const PhotoStudioUtils = {
    // Show notification
    showNotification: function(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.top = '20px';
        alertDiv.style.right = '20px';
        alertDiv.style.zIndex = '9999';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(alertDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 5000);
    },
    
    // Format currency
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('ru-RU', {
            style: 'currency',
            currency: 'RUB'
        }).format(amount);
    },
    
    // Debounce function for performance
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};