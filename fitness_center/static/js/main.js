// Wait for the DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Define our color scheme
    const primaryColor = '#ff3b4e';
    const primaryDark = '#e0323f';
    const secondaryColor = '#222222';
    const lightColor = '#ffffff';
    
    // Apply styling to slider dots
    const sliderDots = document.querySelectorAll('.slider-dot, .dot');
    sliderDots.forEach(dot => {
        dot.style.borderColor = primaryColor;
    });
    
    const activeDots = document.querySelectorAll('.slider-dot.active, .dot.active');
    activeDots.forEach(dot => {
        dot.style.backgroundColor = primaryColor;
        dot.style.borderColor = primaryColor;
    });
    
    // Initialize Bootstrap components
    initBootstrapComponents();
    
    // Add smooth scrolling for navigation links
    initSmoothScroll();
    
    // Handle navbar background change on scroll
    initNavbarScroll();
    
    // Initialize back to top button
    initBackToTop();
    
    // Initialize animation on scroll
    initAnimationOnScroll();
    
    // Initialize any sliders/carousels
    initSliders();
    
    // Add mobile nav toggle functionality
    initMobileNavToggle();
    
    // Handle trainer application modal
    const applicationModal = document.getElementById('applicationModal');
    if (applicationModal) {
        applicationModal.addEventListener('show.bs.modal', function (event) {
            // Get the button that triggered the modal
            const button = event.relatedTarget;
            
            // Extract info from data attributes
            const trainerName = button.getAttribute('data-trainer-name');
            
            // Update the modal content
            const modalTrainerInput = applicationModal.querySelector('#trainer_name');
            if (modalTrainerInput && trainerName) {
                modalTrainerInput.value = trainerName;
            }
            
            const modalTitle = applicationModal.querySelector('.modal-title');
            if (modalTitle && trainerName) {
                modalTitle.textContent = `Запись к тренеру: ${trainerName}`;
            }
        });
    }
    
    // Инициализация слайдера тренеров
    initTrainersSlider();
    
    // Плавная прокрутка к элементам по якорю
    enableSmoothScroll();
    
    // Подсветка активного пункта меню
    highlightActiveMenuItem();
});

// Initialize Bootstrap components that require JavaScript
function initBootstrapComponents() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

// Smooth scrolling for navigation links
function initSmoothScroll() {
    document.querySelectorAll('a.nav-link[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                // Close mobile menu if open
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse && navbarCollapse.classList.contains('show')) {
                    navbarCollapse.classList.remove('show');
                }
                
                // Smooth scroll to target
                window.scrollTo({
                    top: targetElement.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Change navbar background on scroll
function initNavbarScroll() {
    const navbar = document.querySelector('.navbar');
    
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
        
        // Check scroll position on page load
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        }
    }
}

// Back to top button functionality
function initBackToTop() {
    const backToTopButton = document.querySelector('.back-to-top');
    
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
        
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

// Animation on scroll
function initAnimationOnScroll() {
    const animatedElements = document.querySelectorAll('.fade-in, .slide-in-left, .slide-in-right, .zoom-in');
    
    if (animatedElements.length > 0) {
        const animateElement = function() {
            animatedElements.forEach(element => {
                const elementPosition = element.getBoundingClientRect().top;
                const windowHeight = window.innerHeight;
                
                if (elementPosition < windowHeight - 50) {
                    element.classList.add('show');
                }
            });
        };
        
        // Run once on load
        animateElement();
        
        // Run on scroll
        window.addEventListener('scroll', animateElement);
    }
}

// Initialize sliders/carousels
function initSliders() {
    // Trainers slider functionality (simple implementation)
    const trainerSlider = document.querySelector('.trainers-slider');
    if (trainerSlider) {
        const sliderContainer = trainerSlider.querySelector('.trainer-cards');
        const prevButton = trainerSlider.querySelector('.slider-nav.prev');
        const nextButton = trainerSlider.querySelector('.slider-nav.next');
        const dots = trainerSlider.querySelectorAll('.dot');
        
        if (sliderContainer && prevButton && nextButton) {
            let currentSlide = 0;
            const slides = sliderContainer.querySelectorAll('.trainer-card');
            const slideCount = slides.length;
            
            // Set up click handlers for next/prev buttons
            nextButton.addEventListener('click', function() {
                currentSlide = (currentSlide + 1) % slideCount;
                updateSliderPosition();
            });
            
            prevButton.addEventListener('click', function() {
                currentSlide = (currentSlide - 1 + slideCount) % slideCount;
                updateSliderPosition();
            });
            
            // Set up click handlers for dots
            if (dots.length > 0) {
                dots.forEach((dot, index) => {
                    dot.addEventListener('click', function() {
                        currentSlide = index;
                        updateSliderPosition();
                    });
                });
            }
            
            // Update slider position based on current slide
            function updateSliderPosition() {
                const slideWidth = slides[0].offsetWidth + parseInt(getComputedStyle(slides[0]).marginLeft) + parseInt(getComputedStyle(slides[0]).marginRight);
                sliderContainer.style.transform = `translateX(-${currentSlide * slideWidth}px)`;
                
                // Update active dot
                if (dots.length > 0) {
                    dots.forEach((dot, index) => {
                        if (index === currentSlide) {
                            dot.classList.add('active');
                        } else {
                            dot.classList.remove('active');
                        }
                    });
                }
            }
            
            // Initialize slider position
            updateSliderPosition();
            
            // Add touch/swipe support for mobile
            let touchStartX = 0;
            let touchEndX = 0;
            
            sliderContainer.addEventListener('touchstart', function(e) {
                touchStartX = e.changedTouches[0].screenX;
            });
            
            sliderContainer.addEventListener('touchend', function(e) {
                touchEndX = e.changedTouches[0].screenX;
                handleSwipe();
            });
            
            function handleSwipe() {
                const threshold = 50; // Minimum swipe distance
                if (touchStartX - touchEndX > threshold) {
                    // Swipe left, go to next slide
                    nextButton.click();
                } else if (touchEndX - touchStartX > threshold) {
                    // Swipe right, go to previous slide
                    prevButton.click();
                }
            }
        }
    }
}

// Mobile navigation toggle
function initMobileNavToggle() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
    }
}

// Функция инициализации слайдера тренеров
function initTrainersSlider() {
    const sliders = document.querySelectorAll('.trainers-slider');
    
    sliders.forEach(slider => {
        const container = slider.querySelector('.trainers-slider-container');
        const slide = slider.querySelector('.trainer-slide');
        const prevBtn = slider.querySelector('.prev');
        const nextBtn = slider.querySelector('.next');
        const dotsContainer = slider.querySelector('.slider-dots');
        
        if (!container || !slide) return;
        
        // Получаем все карточки тренеров
        const cards = slide.querySelectorAll('.col-md-4');
        if (cards.length === 0) return;
        
        let currentPosition = 0;
        let slidesToShow = getSlidesToShow();
        let slideWidth = 100 / slidesToShow;
        
        // Создаем точки навигации
        updateDots();
        
        // Обработчики событий для кнопок
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                moveSlide(-1);
            });
        }
        
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                moveSlide(1);
            });
        }
        
        // Обновляем при изменении размера окна
        window.addEventListener('resize', () => {
            const newSlidesToShow = getSlidesToShow();
            if (newSlidesToShow !== slidesToShow) {
                slidesToShow = newSlidesToShow;
                slideWidth = 100 / slidesToShow;
                // Корректируем текущую позицию, если нужно
                if (currentPosition > cards.length - slidesToShow) {
                    currentPosition = Math.max(0, cards.length - slidesToShow);
                }
                updateSlidePosition();
                updateDots();
            }
        });
        
        // Определяем количество отображаемых слайдов в зависимости от размера экрана
        function getSlidesToShow() {
            const width = window.innerWidth;
            if (width < 768) return 1;
            if (width < 992) return 2;
            return 3;
        }
        
        // Функция для перемещения слайда
        function moveSlide(direction) {
            currentPosition += direction;
            
            // Циклическая навигация
            if (currentPosition < 0) {
                currentPosition = cards.length - slidesToShow;
            } else if (currentPosition > cards.length - slidesToShow) {
                currentPosition = 0;
            }
            
            updateSlidePosition();
            updateDots();
        }
        
        // Обновляем положение слайдов
        function updateSlidePosition() {
            const translateX = -currentPosition * slideWidth;
            slide.style.transform = `translateX(${translateX}%)`;
        }
        
        // Создаем и обновляем точки навигации
        function updateDots() {
            if (!dotsContainer) return;
            
            // Очищаем контейнер точек
            dotsContainer.innerHTML = '';
            
            // Определяем, сколько точек нужно
            const totalDots = cards.length - slidesToShow + 1;
            
            for (let i = 0; i < totalDots; i++) {
                const dot = document.createElement('span');
                dot.classList.add('slider-dot');
                if (i === currentPosition) {
                    dot.classList.add('active');
                }
                
                dot.addEventListener('click', () => {
                    currentPosition = i;
                    updateSlidePosition();
                    updateDots();
                });
                
                dotsContainer.appendChild(dot);
            }
        }
        
        // Автоматическое прокручивание слайдов каждые 5 секунд
        setInterval(() => {
            moveSlide(1);
        }, 5000);
    });
}

// Функция для плавной прокрутки к элементам
function enableSmoothScroll() {
    const scrollLinks = document.querySelectorAll('a[href^="#"]:not([href="#"])');
    
    scrollLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const navbarHeight = document.querySelector('.navbar').offsetHeight;
                const targetPosition = targetElement.getBoundingClientRect().top + window.pageYOffset - navbarHeight;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Функция для подсветки активного пункта меню при прокрутке
function highlightActiveMenuItem() {
    const sections = document.querySelectorAll('section[id]');
    
    window.addEventListener('scroll', function() {
        let current = '';
        const navbarHeight = document.querySelector('.navbar').offsetHeight;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop - navbarHeight - 50;
            const sectionHeight = section.offsetHeight;
            
            if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });
        
        document.querySelectorAll('.navbar .nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === '#' + current) {
                link.classList.add('active');
            }
        });
    });
} 