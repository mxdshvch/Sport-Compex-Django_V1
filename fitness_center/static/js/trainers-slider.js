/**
 * Trainers Slider for Fitness Center homepage
 * A responsive slider to showcase trainers with touch support
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize trainers slider
    initTrainersSlider();
});

function initTrainersSlider() {
    const sliderContainer = document.querySelector('.trainers-slider-container');
    if (!sliderContainer) return;

    const sliderTrack = sliderContainer.querySelector('.trainers-slider-track');
    const slides = sliderContainer.querySelectorAll('.trainer-card');
    const prevBtn = sliderContainer.querySelector('.slider-prev');
    const nextBtn = sliderContainer.querySelector('.slider-next');
    
    if (!sliderTrack || slides.length === 0) return;
    
    // Slider state
    let currentIndex = 0;
    let slidesToShow = getSlidesToShow();
    let slideWidth = 100 / slidesToShow;
    let touchStartX = 0;
    let touchEndX = 0;
    
    // Set initial styles
    sliderTrack.style.display = 'flex';
    sliderTrack.style.transition = 'transform 0.4s ease-in-out';
    slides.forEach(slide => {
        slide.style.flex = `0 0 ${slideWidth}%`;
        slide.style.padding = '0 10px';
    });
    
    // Initialize slider
    updateSliderPosition();
    
    // Add event listeners
    if (prevBtn) {
        prevBtn.addEventListener('click', goToPrevSlide);
    }
    
    if (nextBtn) {
        nextBtn.addEventListener('click', goToNextSlide);
    }
    
    // Touch support for mobile
    sliderTrack.addEventListener('touchstart', handleTouchStart, false);
    sliderTrack.addEventListener('touchmove', handleTouchMove, false);
    sliderTrack.addEventListener('touchend', handleTouchEnd, false);
    
    // Window resize handling
    window.addEventListener('resize', handleResize);
    
    // Navigation functions
    function goToNextSlide() {
        if (currentIndex < slides.length - slidesToShow) {
            currentIndex++;
            updateSliderPosition();
        } else {
            // Optional: Loop back to the beginning
            currentIndex = 0;
            updateSliderPosition();
        }
    }
    
    function goToPrevSlide() {
        if (currentIndex > 0) {
            currentIndex--;
            updateSliderPosition();
        } else {
            // Optional: Loop to the end
            currentIndex = slides.length - slidesToShow;
            updateSliderPosition();
        }
    }
    
    function updateSliderPosition() {
        const translateX = -currentIndex * slideWidth;
        sliderTrack.style.transform = `translateX(${translateX}%)`;
        updateSliderButtons();
    }
    
    function updateSliderButtons() {
        if (prevBtn) {
            prevBtn.disabled = currentIndex === 0;
            prevBtn.classList.toggle('disabled', currentIndex === 0);
        }
        
        if (nextBtn) {
            const isEnd = currentIndex >= slides.length - slidesToShow;
            nextBtn.disabled = isEnd;
            nextBtn.classList.toggle('disabled', isEnd);
        }
    }
    
    function getSlidesToShow() {
        const windowWidth = window.innerWidth;
        
        if (windowWidth < 576) {
            return 1; // Mobile: 1 slide
        } else if (windowWidth < 992) {
            return 2; // Tablet: 2 slides
        } else {
            return 3; // Desktop: 3 slides
        }
    }
    
    function handleResize() {
        const newSlidesToShow = getSlidesToShow();
        
        if (newSlidesToShow !== slidesToShow) {
            slidesToShow = newSlidesToShow;
            slideWidth = 100 / slidesToShow;
            
            slides.forEach(slide => {
                slide.style.flex = `0 0 ${slideWidth}%`;
            });
            
            // Adjust current index if needed
            if (currentIndex > slides.length - slidesToShow) {
                currentIndex = slides.length - slidesToShow;
            }
            
            updateSliderPosition();
        }
    }
    
    // Touch event handlers
    function handleTouchStart(e) {
        touchStartX = e.touches[0].clientX;
    }
    
    function handleTouchMove(e) {
        touchEndX = e.touches[0].clientX;
    }
    
    function handleTouchEnd() {
        if (!touchStartX || !touchEndX) return;
        
        const touchDiff = touchStartX - touchEndX;
        const threshold = 50; // Minimum swipe distance
        
        if (touchDiff > threshold) {
            goToNextSlide();
        } else if (touchDiff < -threshold) {
            goToPrevSlide();
        }
        
        // Reset touch coordinates
        touchStartX = 0;
        touchEndX = 0;
    }
} 