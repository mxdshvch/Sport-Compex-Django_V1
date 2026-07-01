# Sliders Documentation

This document provides instructions on how to use the sliders implemented in the fitness center website.

## Available Sliders

The project includes the following slider components:

1. **Trainers Slider** - For displaying trainer profiles in a carousel
2. **Services Slider** - For displaying service cards in a responsive carousel

## Common Features

All sliders include:

- Responsive design that adapts to different screen sizes
- Touch swipe support for mobile devices
- Navigation buttons (previous/next)
- Pagination dots for direct slide selection
- Smooth transitions between slides

## How to Implement a Slider

### 1. Include the Required JavaScript

The slider JavaScript files are already included in the base template. If you need to add them to a custom template, include:

```html
<script src="{% static 'js/trainers-slider.js' %}"></script>
<script src="{% static 'js/services-slider.js' %}"></script>
```

### 2. Add the HTML Structure

#### Trainers Slider

```html
<div class="trainers-slider fade-in">
    <div class="trainers-slider-container">
        <!-- Trainer cards -->
        {% for trainer in trainers %}
        <div class="trainer-card">
            <div class="trainer-image-container">
                <img src="{{ trainer.photo.url }}" alt="{{ trainer.name }}" class="trainer-image">
            </div>
            <div class="trainer-info">
                <h4>{{ trainer.name }}</h4>
                <p class="trainer-specialization">{{ trainer.specialization }}</p>
                <p>{{ trainer.bio|truncatechars:100 }}</p>
                <a href="#" class="btn btn-sm btn-outline-primary">Подробнее</a>
            </div>
        </div>
        {% endfor %}
    </div>
    
    <!-- Navigation buttons -->
    <button class="slider-button prev">
        <i class="fas fa-chevron-left"></i>
    </button>
    <button class="slider-button next">
        <i class="fas fa-chevron-right"></i>
    </button>
    
    <!-- Dots navigation -->
    <div class="slider-dots">
        <!-- Dots are generated automatically by JS -->
    </div>
</div>
```

#### Services Slider

```html
<div class="services-slider fade-in">
    <div class="services-slider-container">
        <!-- Service cards -->
        {% for service in services %}
        <div class="service-card">
            <div class="service-icon">
                <i class="fas fa-{{ service.icon }}"></i>
            </div>
            <h3>{{ service.name }}</h3>
            <p>{{ service.description }}</p>
            <a href="#" class="btn btn-outline-primary">Подробнее</a>
        </div>
        {% endfor %}
    </div>
    
    <!-- Navigation buttons -->
    <button class="slider-button prev">
        <i class="fas fa-chevron-left"></i>
    </button>
    <button class="slider-button next">
        <i class="fas fa-chevron-right"></i>
    </button>
    
    <!-- Dots navigation -->
    <div class="slider-dots">
        <!-- Dots are generated automatically by JS -->
    </div>
</div>
```

### 3. Customization

#### CSS Classes

You can customize the appearance of the sliders by modifying their CSS classes in `style.css`:

- Trainers slider styles are under `.trainers-slider` and related classes
- Services slider styles are under `.services-slider` and related classes

#### JavaScript Configuration

If you need to modify the slider behavior, you can adjust the JavaScript files:

- `trainers-slider.js` for trainer slider configuration
- `services-slider.js` for services slider configuration

Key configurable parameters include:
- `slidesToShow` - Number of slides visible at different breakpoints
- Animation speed and transitions
- Swipe sensitivity threshold

## Responsive Behavior

The sliders automatically adapt to different screen sizes:

- **Desktop** (992px and above): Shows 3 slides at once
- **Tablet** (576px to 991px): Shows 2 slides at once
- **Mobile** (below 576px): Shows 1 slide at once

## Animation Effects

The sliders include the following animation effects:

1. Smooth sliding transitions between slides
2. Hover effects on cards
3. Fade-in animation when the slider comes into view (with the `fade-in` class)

## Example Implementation

See the `services_section_example.html` for a complete example of the services slider implementation.

For the trainers slider, refer to the implementation in `templates/workouts/home.html`. 