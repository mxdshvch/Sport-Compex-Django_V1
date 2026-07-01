document.addEventListener('DOMContentLoaded', function() {
    // Initialize services slider
    initServicesSlider();
});

function initServicesSlider() {
    // Get slider elements
    const slider = document.querySelector('.services-slider');
    
    // Only initialize if slider exists on page
    if (!slider) return;
    
    const sliderContainer = slider.querySelector('.services-slider-container');
    const prevButton = slider.querySelector('.slider-button.prev');
    const nextButton = slider.querySelector('.slider-button.next');
    const dotsContainer = slider.querySelector('.slider-dots');
    
    // Get all slides
    const slides = slider.querySelectorAll('.service-card');
    if (!slides.length) return;
    
    // Create track element for smooth transitions
    const track = document.createElement('div');
    track.classList.add('services-track');
    
    // Move all slides into track
    while (sliderContainer.firstChild) {
        track.appendChild(sliderContainer.firstChild);
    }
    
    // Append track to container
    sliderContainer.appendChild(track);
    
    // Variables for slider functionality
    let currentIndex = 0;
    let slidesToShow = 3; // Default for desktop
    let slideWidth = 0;
    let maxIndex = 0;
    
    // Update slider based on screen size
    function updateSliderLayout() {
        // Determine slides to show based on screen width
        if (window.innerWidth < 576) {
            slidesToShow = 1; // Mobile
        } else if (window.innerWidth < 992) {
            slidesToShow = 2; // Tablet
        } else {
            slidesToShow = 3; // Desktop
        }
        
        // Calculate slide width including margins
        const style = window.getComputedStyle(slides[0]);
        const marginRight = parseInt(style.marginRight) || 0;
        const marginLeft = parseInt(style.marginLeft) || 0;
        
        // Calculate total width of container
        const containerWidth = sliderContainer.clientWidth;
        
        // Calculate slide width based on container and slides to show
        slideWidth = (containerWidth / slidesToShow) - (marginRight + marginLeft);
        
        // Set width for all slides
        slides.forEach(slide => {
            slide.style.minWidth = `${slideWidth}px`;
            slide.style.maxWidth = `${slideWidth}px`;
        });
        
        // Calculate max index (total slides - visible slides)
        maxIndex = Math.max(0, slides.length - slidesToShow);
        
        // Ensure current index is not beyond max
        if (currentIndex > maxIndex) {
            currentIndex = maxIndex;
        }
        
        // Update track position
        updateTrackPosition();
        
        // Generate dots based on number of possible slide positions
        generateDots();
    }
    
    // Update track position based on current index
    function updateTrackPosition() {
        const style = window.getComputedStyle(slides[0]);
        const marginRight = parseInt(style.marginRight) || 0;
        const totalSlideWidth = slideWidth + marginRight;
        track.style.transform = `translateX(-${currentIndex * totalSlideWidth}px)`;
        
        // Update dots to show active
        updateActiveDot();
        
        // Update button states
        updateButtonStates();
    }
    
    // Generate pagination dots
    function generateDots() {
        // Clear existing dots
        dotsContainer.innerHTML = '';
        
        // Create a dot for each possible slide position
        for (let i = 0; i <= maxIndex; i++) {
            const dot = document.createElement('span');
            dot.classList.add('dot');
            if (i === currentIndex) {
                dot.classList.add('active');
            }
            
            // Add click event to go to specific slide
            dot.addEventListener('click', () => {
                currentIndex = i;
                updateTrackPosition();
            });
            
            dotsContainer.appendChild(dot);
        }
    }
    
    // Update active dot based on current index
    function updateActiveDot() {
        const dots = dotsContainer.querySelectorAll('.dot');
        dots.forEach((dot, index) => {
            if (index === currentIndex) {
                dot.classList.add('active');
            } else {
                dot.classList.remove('active');
            }
        });
    }
    
    // Update prev/next button states
    function updateButtonStates() {
        prevButton.disabled = currentIndex === 0;
        nextButton.disabled = currentIndex === maxIndex;
        
        // Visual feedback
        if (currentIndex === 0) {
            prevButton.classList.add('disabled');
        } else {
            prevButton.classList.remove('disabled');
        }
        
        if (currentIndex === maxIndex) {
            nextButton.classList.add('disabled');
        } else {
            nextButton.classList.remove('disabled');
        }
    }
    
    // Event handlers for buttons
    if (prevButton) {
        prevButton.addEventListener('click', () => {
            if (currentIndex > 0) {
                currentIndex--;
                updateTrackPosition();
            }
        });
    }
    
    if (nextButton) {
        nextButton.addEventListener('click', () => {
            if (currentIndex < maxIndex) {
                currentIndex++;
                updateTrackPosition();
            }
        });
    }
    
    // Add touch support for mobile
    let touchStartX = 0;
    let touchEndX = 0;
    
    sliderContainer.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
    });
    
    sliderContainer.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        
        // Calculate swipe direction and distance
        const diff = touchStartX - touchEndX;
        const threshold = 50; // Min swipe distance
        
        if (Math.abs(diff) > threshold) {
            if (diff > 0 && currentIndex < maxIndex) {
                // Swipe left - next slide
                currentIndex++;
                updateTrackPosition();
            } else if (diff < 0 && currentIndex > 0) {
                // Swipe right - previous slide
                currentIndex--;
                updateTrackPosition();
            }
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', updateSliderLayout);
    
    // Initialize layout
    updateSliderLayout();
} 