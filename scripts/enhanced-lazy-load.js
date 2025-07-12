/**
 * enhanced lazy loading with webp support and performance optimizations
 * for loyal.love-website
 */

class EnhancedLazyLoader {
    constructor() {
        this.images = [];
        this.observer = null;
        this.webpSupported = this.checkWebPSupport();
        this.init();
    }

    checkWebPSupport() {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    }

    init() {
        // add loading="lazy" to all images that don't have it
        const images = document.querySelectorAll('img:not([loading])');
        images.forEach(img => {
            img.setAttribute('loading', 'lazy');
        });

        // get all lazy images
        this.images = document.querySelectorAll('img[loading="lazy"]');
        
        // set up intersection observer
        this.setupObserver();
        
        // preload critical images (first few images)
        this.preloadCriticalImages();
        
        // add error handling
        this.addErrorHandling();
    }

    setupObserver() {
        if ('IntersectionObserver' in window) {
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.loadImage(entry.target);
                        this.observer.unobserve(entry.target);
                    }
                });
            }, {
                rootMargin: '50px 0px', // start loading 50px before image enters viewport
                threshold: 0.01
            });

            this.images.forEach(img => {
                this.observer.observe(img);
            });
        } else {
            // fallback for older browsers
            this.images.forEach(img => {
                this.loadImage(img);
            });
        }
    }

    loadImage(img) {
        // check if image is already loaded
        if (img.classList.contains('loaded') || img.classList.contains('loading')) {
            return;
        }

        img.classList.add('loading');

        // try to load webp version first if supported
        if (this.webpSupported) {
            const webpSrc = this.getWebPSrc(img.src);
            if (webpSrc) {
                this.loadImageWithFallback(img, webpSrc, img.src);
                return;
            }
        }

        // load original image
        this.loadImageDirect(img);
    }

    getWebPSrc(originalSrc) {
        // check if webp version exists
        const webpSrc = originalSrc.replace(/\.(jpg|jpeg|png)$/i, '_webp.webp');
        
        // for now, we'll assume webp versions exist if they were created by the optimization script
        // in production, you might want to check if the file actually exists
        return webpSrc;
    }

    loadImageWithFallback(img, webpSrc, fallbackSrc) {
        const webpImg = new Image();
        
        webpImg.onload = () => {
            img.src = webpSrc;
            img.classList.add('loaded');
            img.classList.remove('loading');
        };
        
        webpImg.onerror = () => {
            // webp failed, fall back to original
            this.loadImageDirect(img);
        };
        
        webpImg.src = webpSrc;
    }

    loadImageDirect(img) {
        const originalSrc = img.src;
        
        // add a small delay to prevent overwhelming the browser
        setTimeout(() => {
            img.onload = () => {
                img.classList.add('loaded');
                img.classList.remove('loading');
            };
            
            img.onerror = () => {
                img.classList.add('error');
                img.classList.remove('loading');
                console.warn(`Failed to load image: ${originalSrc}`);
            };
            
            // trigger load if src is already set
            if (img.src) {
                img.src = img.src;
            }
        }, Math.random() * 100); // random delay to prevent thundering herd
    }

    preloadCriticalImages() {
        // preload first 3 images for better perceived performance
        const criticalImages = Array.from(this.images).slice(0, 3);
        
        criticalImages.forEach(img => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.as = 'image';
            link.href = img.src;
            document.head.appendChild(link);
        });
    }

    addErrorHandling() {
        // add global error handling for images
        document.addEventListener('error', (e) => {
            if (e.target.tagName === 'IMG') {
                e.target.classList.add('error');
                e.target.classList.remove('loading');
                
                // add a placeholder or retry mechanism
                this.handleImageError(e.target);
            }
        }, true);
    }

    handleImageError(img) {
        // add a subtle error indicator
        img.style.opacity = '0.5';
        img.style.filter = 'grayscale(100%)';
        
        // add retry button for failed images
        const retryBtn = document.createElement('button');
        retryBtn.textContent = 'Retry';
        retryBtn.className = 'image-retry-btn';
        retryBtn.onclick = () => {
            img.classList.remove('error');
            img.style.opacity = '';
            img.style.filter = '';
            retryBtn.remove();
            this.loadImage(img);
        };
        
        img.parentNode.insertBefore(retryBtn, img.nextSibling);
    }

    // public method to manually load an image
    loadImageNow(img) {
        if (this.observer) {
            this.observer.unobserve(img);
        }
        this.loadImage(img);
    }

    // public method to refresh all images
    refresh() {
        this.images = document.querySelectorAll('img[loading="lazy"]');
        this.setupObserver();
    }
}

// initialize when dom is ready
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedLazyLoader = new EnhancedLazyLoader();
});

// add css for error states
const style = document.createElement('style');
style.textContent = `
    img[loading="lazy"] {
        opacity: 0;
        transition: opacity 0.3s ease-in-out;
    }
    
    img[loading="lazy"].loaded {
        opacity: 1;
    }
    
    img[loading="lazy"].loading {
        opacity: 0.3;
    }
    
    img[loading="lazy"].error {
        opacity: 0.5;
        filter: grayscale(100%);
    }
    
    .image-retry-btn {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: rgba(0, 0, 0, 0.7);
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        z-index: 10;
    }
    
    .image-retry-btn:hover {
        background: rgba(0, 0, 0, 0.9);
    }
`;
document.head.appendChild(style);
