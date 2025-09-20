// ANZx.ai - Interactive Website

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 ANZx.ai Loading...');
    
    // Initialize all interactive features
    initMouseEffects();
    initScrollAnimations();
    initNavigation();
    initInteractiveCanvas();
    
    console.log('✨ ANZx.ai Loaded Successfully!');
});

// Mouse Effects
function initMouseEffects() {
    let mouseX = 0;
    let mouseY = 0;
    
    // Track mouse movement
    document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        // Update CSS custom properties for mouse-based effects
        document.documentElement.style.setProperty('--mouse-x', mouseX + 'px');
        document.documentElement.style.setProperty('--mouse-y', mouseY + 'px');
        
        // Create mouse trail effect
        createMouseTrail(e);
        
        // Update parallax effect
        updateParallax(e);
    });
    
    // Mouse trail
    function createMouseTrail(e) {
        if (Math.random() > 0.8) { // Only create trail sometimes for performance
            const trail = document.createElement('div');
            trail.style.position = 'fixed';
            trail.style.left = e.clientX - 3 + 'px';
            trail.style.top = e.clientY - 3 + 'px';
            trail.style.width = '6px';
            trail.style.height = '6px';
            trail.style.background = 'rgba(102, 126, 234, 0.6)';
            trail.style.borderRadius = '50%';
            trail.style.pointerEvents = 'none';
            trail.style.zIndex = '9998';
            trail.style.animation = 'trailFade 0.8s ease-out forwards';
            
            document.body.appendChild(trail);
            
            setTimeout(() => {
                if (trail.parentNode) {
                    trail.remove();
                }
            }, 800);
        }
    }
    
    // Parallax effect for floating circles
    function updateParallax(e) {
        const circles = document.querySelectorAll('.floating-circle');
        const centerX = window.innerWidth / 2;
        const centerY = window.innerHeight / 2;
        const deltaX = (e.clientX - centerX) / centerX;
        con     const node2 = this.neuralNodes[j];
                const distance = Math.sqrt(
                    Math.pow(node1.x - node2.x, 2) + Math.pow(node1.y - node2.y, 2)
                );
                
                if (distance < 30) {
                    const connection = document.createElement('div');
                    connection.className = 'neural-connection';
                    
                    const angle = Math.atan2(node2.y - node1.y, node2.x - node1.x);
                    const length = distance * (window.innerWidth / 100);
                    
                    connection.style.left = node1.x + '%';
                    connection.style.top = node1.y + '%';
                    connection.style.width = length + 'px';
                    connection.style.transform = `rotate(${angle}rad)`;
                    connection.style.animationDelay = Math.random() * 4 + 's';
                    
                    container.appendChild(connection);
                }
            }
        }
    }
    
    createFloatingOrbs() {
        const container = document.getElementById('floating-orbs');
        if (!container) return;
        
        for (let i = 0; i < 6; i++) {
            const orb = document.createElement('div');
            orb.className = 'orb';
            
            const size = 20 + Math.random() * 60;
            orb.style.width = size + 'px';
            orb.style.height = size + 'px';
            orb.style.left = Math.random() * 100 + '%';
            orb.style.top = Math.random() * 100 + '%';
            orb.style.animationDelay = Math.random() * 20 + 's';
            orb.style.animationDuration = (15 + Math.random() * 10) + 's';
            
            container.appendChild(orb);
            this.orbs.push(orb);
        }
    }
    
    createMatrixRain() {
        const container = document.getElementById('matrix-rain');
        if (!container) return;
        
        const characters = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
        
        for (let i = 0; i < 15; i++) {
            const column = document.createElement('div');
            column.className = 'matrix-column';
            column.style.left = Math.random() * 100 + '%';
            column.style.animationDuration = (8 + Math.random() * 12) + 's';
            column.style.animationDelay = Math.random() * 10 + 's';
            
            let text = '';
            for (let j = 0; j < 20; j++) {
                text += characters[Math.floor(Math.random() * characters.length)] + '<br>';
            }
            column.innerHTML = text;
            
            container.appendChild(column);
            this.matrixColumns.push(column);
        }
    }
    
    createGeometricShapes() {
        const container = document.getElementById('geometric-shapes');
        if (!container) return;
        
        const shapes = ['triangle', 'square', 'circle', 'hexagon'];
        
        for (let i = 0; i < 12; i++) {
            const shape = document.createElement('div');
            const shapeType = shapes[Math.floor(Math.random() * shapes.length)];
            shape.className = `geometric-shape ${shapeType}`;
            
            shape.style.left = Math.random() * 100 + '%';
            shape.style.top = Math.random() * 100 + '%';
            shape.style.animationDelay = Math.random() * 25 + 's';
            shape.style.animationDuration = (20 + Math.random() * 10) + 's';
            
            container.appendChild(shape);
            this.geometricShapes.push(shape);
        }
    }
    
    bindEvents() {
        // Mouse movement tracking
        document.addEventListener('mousemove', (e) => {
            this.mouseX = e.clientX;
            this.mouseY = e.clientY;
            this.isMouseMoving = true;
            
            this.updateCustomCursor(e);
            this.createMouseTrail(e);
            this.updateParallaxEffect(e);
            
            clearTimeout(this.mouseStopTimeout);
            this.mouseStopTimeout = setTimeout(() => {
                this.isMouseMoving = false;
            }, 100);
        });
        
        // Hover effects
        document.addEventListener('mouseenter', (e) => {
            if (e.target.matches('a, button, .btn')) {
                this.cursor.classList.add('hover');
            }
        });
        
        document.addEventListener('mouseleave', (e) => {
            if (e.target.matches('a, button, .btn')) {
                this.cursor.classList.remove('hover');
            }
        });
        
        // Click effects
        document.addEventListener('click', (e) => {
            this.createClickRipple(e);
        });
        
        // Scroll effects
        window.addEventListener('scroll', () => {
            this.updateScrollEffects();
        });
        
        // Resize handling
        window.addEventListener('resize', () => {
            this.handleResize();
        });
    }
    
    updateCustomCursor(e) {
        this.cursor.style.left = e.clientX - 10 + 'px';
        this.cursor.style.top = e.clientY - 10 + 'px';
    }
    
    createMouseTrail(e) {
        if (Math.random() > 0.7) { // Only create trail sometimes for performance
            const trail = document.createElement('div');
            trail.className = 'mouse-trail';
            trail.style.left = e.clientX - 3 + 'px';
            trail.style.top = e.clientY - 3 + 'px';
            
            document.body.appendChild(trail);
            
            setTimeout(() => {
                trail.remove();
            }, 500);
        }
    }
    
    updateParallaxEffect(e) {
        const centerX = window.innerWidth / 2;
        const centerY = window.innerHeight / 2;
        const deltaX = (e.clientX - centerX) / centerX;
        const deltaY = (e.clientY - centerY) / centerY;
        
        // Update neural network
        const neuralNetwork = document.getElementById('neural-network');
        if (neuralNetwork) {
            neuralNetwork.style.transform = `translate(${deltaX * 20}px, ${deltaY * 20}px)`;
        }
        
        // Update floating orbs
        this.orbs.forEach((orb, index) => {
            const multiplier = (index + 1) * 0.5;
            orb.style.transform = `translate(${deltaX * 10 * multiplier}px, ${deltaY * 10 * multiplier}px)`;
        });
        
        // Update geometric shapes
        this.geometricShapes.forEach((shape, index) => {
            const multiplier = (index % 3 + 1) * 0.3;
            shape.style.transform = `translate(${deltaX * 15 * multiplier}px, ${deltaY * 15 * multiplier}px) rotate(${deltaX * 45}deg)`;
        });
    }
    
    createClickRipple(e) {
        const ripple = document.createElement('div');
        ripple.style.position = 'fixed';
        ripple.style.left = e.clientX - 25 + 'px';
        ripple.style.top = e.clientY - 25 + 'px';
        ripple.style.width = '50px';
        ripple.style.height = '50px';
        ripple.style.borderRadius = '50%';
        ripple.style.background = 'radial-gradient(circle, rgba(102, 126, 234, 0.3), transparent)';
        ripple.style.pointerEvents = 'none';
        ripple.style.zIndex = '9999';
        ripple.style.animation = 'rippleEffect 0.6s ease-out forwards';
        
        document.body.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
    
    updateScrollEffects() {
        const scrollY = window.scrollY;
        const windowHeight = window.innerHeight;
        
        // Parallax background elements
        const heroBackground = document.querySelector('.hero-background');
        if (heroBackground) {
            heroBackground.style.transform = `translateY(${scrollY * 0.5}px)`;
        }
        
        // Fade out hero elements on scroll
        const heroContent = document.querySelector('.hero-content');
        if (heroContent) {
            const opacity = Math.max(0, 1 - (scrollY / windowHeight));
            heroContent.style.opacity = opacity;
        }
    }
    
    handleResize() {
        // Recalculate positions and update animations
        this.updateNeuralConnections();
    }
    
    startAnimationLoop() {
        const animate = () => {
            // Update neural node positions
            this.neuralNodes.forEach(node => {
                node.x += node.vx;
                node.y += node.vy;
                
                // Bounce off edges
                if (node.x <= 0 || node.x >= 100) node.vx *= -1;
                if (node.y <= 0 || node.y >= 100) node.vy *= -1;
                
                // Keep within bounds
                node.x = Math.max(0, Math.min(100, node.x));
                node.y = Math.max(0, Math.min(100, node.y));
                
                node.element.style.left = node.x + '%';
                node.element.style.top = node.y + '%';
            });
            
            requestAnimationFrame(animate);
        };
        
        animate();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize advanced animation engine
    const animationEngine = new AdvancedAnimationEngine();
    
    // Add ripple effect keyframes
    const style = document.createElement('style');
    style.textContent = `
        @keyframes rippleEffect {
            0% {
                transform: scale(0);
                opacity: 1;
            }
            100% {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Mobile Navigation Toggle
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            navToggle.classList.toggle('active');
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Close mobile menu if open
                if (navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    navToggle.classList.remove('active');
                }
            }
        });
    });
    
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', function() {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > 100) {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.backdropFilter = 'blur(20px)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.8)';
            navbar.style.backdropFilter = 'blur(20px)';
        }
        
        lastScrollY = currentScrollY;
    });
    
    // Animate elements on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.solution-card, .platform-feature, .stat-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    // Contact form handling
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(contactForm);
            const data = Object.fromEntries(formData);
            
            // Show loading state
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Sending...';
            submitBtn.disabled = true;
            
            // Simulate form submission (replace with actual API call)
            setTimeout(() => {
                alert('Thank you for your message! We\'ll get back to you soon.');
                contactForm.reset();
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }, 2000);
        });
    }
    
    // Hero particles animation
    const heroParticles = document.querySelector('.hero-particles');
    if (heroParticles) {
        // Add floating animation with mouse interaction
        document.addEventListener('mousemove', function(e) {
            const x = (e.clientX / window.innerWidth) * 100;
            const y = (e.clientY / window.innerHeight) * 100;
            
            heroParticles.style.transform = `translate(${x * 0.02}px, ${y * 0.02}px)`;
        });
    }
    
    // Typing animation for hero title
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        const gradientText = heroTitle.querySelector('.hero-gradient-text');
        if (gradientText) {
            const text = gradientText.textContent;
            gradientText.textContent = '';
            
            let i = 0;
            const typeWriter = () => {
                if (i < text.length) {
                    gradientText.textContent += text.charAt(i);
                    i++;
                    setTimeout(typeWriter, 100);
                }
            };
            
            // Start typing animation after a delay
            setTimeout(typeWriter, 1000);
        }
    }
    
    // Agent card hover effects
    document.querySelectorAll('.agent-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = '0 10px 25px -5px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '';
        });
    });
    
    // Dashboard stats counter animation
    const animateCounter = (element, target, duration = 2000) => {
        const start = 0;
        const increment = target / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            
            // Format number based on type
            if (element.textContent.includes('%')) {
                element.textContent = Math.round(current * 10) / 10 + '%';
            } else if (element.textContent.includes('s')) {
                element.textContent = Math.round(current * 10) / 10 + 's';
            } else if (target > 1000) {
                element.textContent = Math.round(current).toLocaleString();
            } else {
                element.textContent = Math.round(current);
            }
        }, 16);
    };
    
    // Animate dashboard stats when visible
    const dashboardObserver = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const statNumbers = entry.target.querySelectorAll('.stat-number');
                statNumbers.forEach(stat => {
                    const text = stat.textContent;
                    const number = parseFloat(text.replace(/[^\d.]/g, ''));
                    if (number) {
                        animateCounter(stat, number);
                    }
                });
                dashboardObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    const dashboard = document.querySelector('.platform-dashboard');
    if (dashboard) {
        dashboardObserver.observe(dashboard);
    }
    
    // Add loading states for buttons
    document.querySelectorAll('.btn-primary').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.href && this.href.includes('/auth/')) {
                e.preventDefault();
                
                // Add loading state
                const originalText = this.innerHTML;
                this.innerHTML = '<span>Loading...</span>';
                this.style.pointerEvents = 'none';
                
                // Simulate navigation delay
                setTimeout(() => {
                    window.location.href = this.href;
                }, 1000);
            }
        });
    });
    
    // Initialize tooltips (if needed)
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        });
        
        element.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
});

// Utility functions
function debounce(func, wait) {
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

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Performance optimization
const debouncedResize = debounce(() => {
    // Handle resize events
    console.log('Window resized');
}, 250);

window.addEventListener('resize', debouncedResize);   
 // Advanced Interactive Features
    
    // Magnetic Effect for Interactive Elements
    function initMagneticEffect() {
        const magneticElements = document.querySelectorAll('.magnetic, .btn, .agent-card');
        
        magneticElements.forEach(element => {
            element.addEventListener('mousemove', (e) => {
                const rect = element.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;
                
                const strength = 0.3;
                element.style.transform = `translate(${x * strength}px, ${y * strength}px) scale(1.05)`;
            });
            
            element.addEventListener('mouseleave', () => {
                element.style.transform = 'translate(0, 0) scale(1)';
            });
        });
    }
    
    // Particle System
    function createParticleSystem() {
        const particleContainer = document.createElement('div');
        particleContainer.style.position = 'fixed';
        particleContainer.style.top = '0';
        particleContainer.style.left = '0';
        particleContainer.style.width = '100%';
        particleContainer.style.height = '100%';
        particleContainer.style.pointerEvents = 'none';
        particleContainer.style.zIndex = '-1';
        document.body.appendChild(particleContainer);
        
        function createParticle() {
            const particle = document.createElement('div');
            particle.className = 'particle';
            
            const size = Math.random() * 4 + 2;
            particle.style.width = size + 'px';
            particle.style.height = size + 'px';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.background = `rgba(${102 + Math.random() * 50}, ${126 + Math.random() * 50}, ${234}, ${Math.random() * 0.5 + 0.2})`;
            particle.style.animationDuration = (Math.random() * 3 + 2) + 's';
            particle.style.animationDelay = Math.random() * 2 + 's';
            
            particleContainer.appendChild(particle);
            
            setTimeout(() => {
                particle.remove();
            }, 5000);
        }
        
        // Create particles periodically
        setInterval(createParticle, 300);
    }
    
    // Scroll Reveal Animation
    function initScrollReveal() {
        const revealElements = document.querySelectorAll('.solution-card, .platform-feature, .stat-card');
        
        revealElements.forEach((element, index) => {
            element.classList.add('scroll-reveal');
            if (index % 2 === 0) {
                element.classList.add('slide-left');
            } else {
                element.classList.add('slide-right');
            }
        });
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add('revealed');
                    }, index * 100);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        revealElements.forEach(element => {
            observer.observe(element);
        });
    }
    
    // Typing Animation
    function initTypingAnimation() {
        const typingElements = document.querySelectorAll('[data-typing]');
        
        typingElements.forEach(element => {
            const text = element.getAttribute('data-typing');
            element.textContent = '';
            element.classList.add('typing-text');
            
            let i = 0;
            const typeWriter = () => {
                if (i < text.length) {
                    element.textContent += text.charAt(i);
                    i++;
                    setTimeout(typeWriter, 100);
                } else {
                    element.style.borderRight = 'none';
                }
            };
            
            // Start typing when element is visible
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        setTimeout(typeWriter, 500);
                        observer.unobserve(entry.target);
                    }
                });
            });
            
            observer.observe(element);
        });
    }
    
    // 3D Card Effect
    function init3DCards() {
        const cards = document.querySelectorAll('.solution-card, .agent-card');
        
        cards.forEach(card => {
            card.classList.add('card-3d');
            const inner = document.createElement('div');
            inner.className = 'card-3d-inner';
            
            // Move all card content to inner div
            while (card.firstChild) {
                inner.appendChild(card.firstChild);
            }
            card.appendChild(inner);
            
            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                
                const centerX = rect.width / 2;
                const centerY = rect.height / 2;
                
                const rotateX = (y - centerY) / 10;
                const rotateY = (centerX - x) / 10;
                
                inner.style.transform = `rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
            });
            
            card.addEventListener('mouseleave', () => {
                inner.style.transform = 'rotateX(0) rotateY(0)';
            });
        });
    }
    
    // Liquid Morphing Shapes
    function createLiquidShapes() {
        const hero = document.querySelector('.hero');
        if (!hero) return;
        
        for (let i = 0; i < 3; i++) {
            const shape = document.createElement('div');
            shape.className = 'liquid-shape';
            
            const size = 200 + Math.random() * 300;
            shape.style.width = size + 'px';
            shape.style.height = size + 'px';
            shape.style.left = Math.random() * 100 + '%';
            shape.style.top = Math.random() * 100 + '%';
            shape.style.animationDelay = Math.random() * 8 + 's';
            shape.style.animationDuration = (6 + Math.random() * 4) + 's';
            
            hero.appendChild(shape);
        }
    }
    
    // Advanced Mouse Interactions
    function initAdvancedMouseEffects() {
        let mouseX = 0;
        let mouseY = 0;
        let isMouseMoving = false;
        
        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            isMouseMoving = true;
            
            // Update CSS custom properties for mouse position
            document.documentElement.style.setProperty('--mouse-x', mouseX + 'px');
            document.documentElement.style.setProperty('--mouse-y', mouseY + 'px');
            
            // Create dynamic lighting effect
            const hero = document.querySelector('.hero');
            if (hero) {
                const rect = hero.getBoundingClientRect();
                const x = ((mouseX - rect.left) / rect.width) * 100;
                const y = ((mouseY - rect.top) / rect.height) * 100;
                
                hero.style.background = `radial-gradient(circle at ${x}% ${y}%, 
                    rgba(102, 126, 234, 0.1) 0%, 
                    rgba(240, 147, 251, 0.05) 50%, 
                    transparent 70%)`;
            }
            
            clearTimeout(window.mouseStopTimeout);
            window.mouseStopTimeout = setTimeout(() => {
                isMouseMoving = false;
            }, 100);
        });
    }
    
    // Performance Monitor
    function initPerformanceMonitor() {
        let fps = 0;
        let lastTime = performance.now();
        
        function calculateFPS() {
            const currentTime = performance.now();
            fps = 1000 / (currentTime - lastTime);
            lastTime = currentTime;
            
            // Reduce animations if FPS is too low
            if (fps < 30) {
                document.body.classList.add('low-performance');
            } else {
                document.body.classList.remove('low-performance');
            }
            
            requestAnimationFrame(calculateFPS);
        }
        
        calculateFPS();
    }
    
    // Initialize all advanced features
    initMagneticEffect();
    createParticleSystem();
    initScrollReveal();
    initTypingAnimation();
    init3DCards();
    createLiquidShapes();
    initAdvancedMouseEffects();
    initPerformanceMonitor();
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Close mobile menu if open
                if (navMenu && navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    navToggle.classList.remove('active');
                }
            }
        });
    });
    
    // Navbar scroll effect with advanced styling
    const navbar = document.querySelector('.navbar');
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', function() {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > 100) {
            navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            navbar.style.backdropFilter = 'blur(20px)';
            navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
        } else {
            navbar.style.background = 'rgba(255, 255, 255, 0.8)';
            navbar.style.backdropFilter = 'blur(20px)';
            navbar.style.boxShadow = 'none';
        }
        
        // Hide/show navbar on scroll
        if (currentScrollY > lastScrollY && currentScrollY > 200) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollY = currentScrollY;
    });
    
    // Enhanced contact form
    const contactForm = document.getElementById('contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            // Animated loading state
            submitBtn.innerHTML = '<span class="loading-spinner"></span> Sending...';
            submitBtn.disabled = true;
            
            // Add loading spinner styles
            const style = document.createElement('style');
            style.textContent = `
                .loading-spinner {
                    display: inline-block;
                    width: 16px;
                    height: 16px;
                    border: 2px solid rgba(255,255,255,0.3);
                    border-radius: 50%;
                    border-top-color: white;
                    animation: spin 1s ease-in-out infinite;
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
            
            // Simulate form submission
            setTimeout(() => {
                submitBtn.innerHTML = '✓ Message Sent!';
                submitBtn.style.background = 'var(--success)';
                
                setTimeout(() => {
                    contactForm.reset();
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                    submitBtn.style.background = '';
                    style.remove();
                }, 2000);
            }, 2000);
        });
    }
    
    // Add GPU acceleration to animated elements
    document.querySelectorAll('.hero-particles, .neural-network, .floating-orbs, .ai-interface').forEach(element => {
        element.classList.add('gpu-accelerated');
    });
    
    console.log('🚀 ANZx.ai Advanced Animation Engine Loaded!');
});

// Utility functions for advanced effects
function createRippleEffect(element, event) {
    const ripple = document.createElement('span');
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    element.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Add ripple effect to buttons
document.addEventListener('click', function(e) {
    if (e.target.matches('.btn, button')) {
        createRippleEffect(e.target, e);
    }
});

// Performance optimization for low-end devices
if (navigator.hardwareConcurrency < 4 || navigator.deviceMemory < 4) {
    document.body.classList.add('low-performance');
}