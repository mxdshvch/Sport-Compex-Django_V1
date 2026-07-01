document.addEventListener('DOMContentLoaded', function() {
    // Initialize trainer grid animations
    initTrainersGrid();
});

function initTrainersGrid() {
    const trainerCards = document.querySelectorAll('.trainer-card-modern');
    
    if (!trainerCards.length) return;
    
    // Add staggered animation on page load
    trainerCards.forEach((card, index) => {
        // Add a slight delay for each card
        setTimeout(() => {
            card.classList.add('show');
        }, 100 * index);
    });
    
    // Add hover sound effect for trainers if audio support is enabled
    const audioEnabled = false; // Set to true to enable sound effects
    if (audioEnabled) {
        const hoverSound = new Audio('/static/sounds/hover.mp3');
        
        trainerCards.forEach(card => {
            card.addEventListener('mouseenter', () => {
                hoverSound.volume = 0.2;
                hoverSound.currentTime = 0;
                hoverSound.play().catch(e => {
                    // Silently fail if audio cannot be played
                    console.log('Audio autoplay prevented by browser');
                });
            });
        });
    }
    
    // Add click handler for trainer cards
    trainerCards.forEach(card => {
        // Handle clicks on the "Записаться" button
        const bookButton = card.querySelector('.btn');
        if (bookButton) {
            bookButton.addEventListener('click', function(e) {
                // The modal is handled by Bootstrap, but we can add custom behavior
                const trainerName = this.getAttribute('data-trainer-name');
                
                // You can track analytics events here
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'trainer_booking_click', {
                        'trainer_name': trainerName
                    });
                }
                
                // Highlight the clicked card
                trainerCards.forEach(c => c.classList.remove('selected'));
                card.classList.add('selected');
            });
        }
    });
    
    // Add filter functionality if trainer filters exist
    const trainerFilters = document.querySelectorAll('.trainer-filter');
    if (trainerFilters.length) {
        trainerFilters.forEach(filter => {
            filter.addEventListener('click', function() {
                const specialization = this.getAttribute('data-specialization');
                
                // Remove active class from all filters and add to clicked one
                trainerFilters.forEach(f => f.classList.remove('active'));
                this.classList.add('active');
                
                if (specialization === 'all') {
                    // Show all trainers
                    trainerCards.forEach(card => {
                        card.style.display = 'block';
                        setTimeout(() => {
                            card.classList.add('show');
                        }, 50);
                    });
                } else {
                    // Filter trainers by specialization
                    trainerCards.forEach(card => {
                        const cardSpec = card.querySelector('.trainer-specialization').textContent.toLowerCase();
                        
                        if (cardSpec.includes(specialization.toLowerCase())) {
                            card.style.display = 'block';
                            setTimeout(() => {
                                card.classList.add('show');
                            }, 50);
                        } else {
                            card.classList.remove('show');
                            setTimeout(() => {
                                card.style.display = 'none';
                            }, 300); // Match the transition duration
                        }
                    });
                }
            });
        });
    }
    
    // Add scroll animation for trainer details
    const trainerDetails = document.querySelectorAll('.trainer-details');
    if (trainerDetails.length) {
        window.addEventListener('scroll', () => {
            trainerDetails.forEach(details => {
                const position = details.getBoundingClientRect();
                
                // If element is in viewport
                if (position.top < window.innerHeight && position.bottom >= 0) {
                    details.classList.add('animate');
                }
            });
        });
    }
}

// Add CSS class for the animation
document.head.insertAdjacentHTML('beforeend', `
<style>
    .trainer-card-modern {
        opacity: 0;
        transform: translateY(30px);
        transition: opacity 0.5s ease, transform 0.5s ease, box-shadow 0.4s ease;
    }
    
    .trainer-card-modern.show {
        opacity: 1;
        transform: translateY(0);
    }
    
    .trainer-card-modern.selected {
        box-shadow: 0 15px 40px rgba(255, 0, 0, 0.4);
    }
    
    .trainer-details {
        transform: translateY(20px);
        opacity: 0.8;
        transition: transform 0.4s ease, opacity 0.4s ease;
    }
    
    .trainer-details.animate,
    .trainer-card-modern:hover .trainer-details {
        transform: translateY(0);
        opacity: 1;
    }
    
    .trainer-filter {
        display: inline-block;
        padding: 8px 16px;
        margin: 0 5px 10px;
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border-radius: 4px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .trainer-filter:hover,
    .trainer-filter.active {
        background-color: var(--primary);
    }
</style>
`); 