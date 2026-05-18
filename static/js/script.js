// تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    // تأثيرات الانتقال الناعمة
    initPageTransitions();
    
    // تأكيد الحذف
    initDeleteConfirmations();
    
    // تحسين التفاعلات
    initUIEnhancements();
    
    // إخفاء الرسائل التلقائي
    autoHideAlerts();
    
    // تحسين النماذج
    initFormEnhancements();
    
    // تأثيرات تحميل الصفحة الجديدة
    initAdvancedAnimations();
    
    // تأثيرات التمرير
    initScrollAnimations();
});

// تأثيرات الانتقال المطورة
function initPageTransitions() {
    // إضافة تأثير fade in للمحتوى مع bounce effect
    const content = document.querySelector('.content-wrapper, .main-content, .container');
    if (content) {
        content.style.opacity = '0';
        content.style.transform = 'translateY(30px) scale(0.95)';
        
        setTimeout(() => {
            content.style.transition = 'all 0.8s cubic-bezier(0.4, 0.0, 0.2, 1)';
            content.style.opacity = '1';
            content.style.transform = 'translateY(0) scale(1)';
        }, 150);
    }
    
    // تأثير متدرج للكروت مع stagger effect
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(40px) rotateX(10deg)';
        card.style.filter = 'blur(5px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.7s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0) rotateX(0deg)';
            card.style.filter = 'blur(0px)';
        }, 300 + (index * 120));
    });
    
    // تأثيرات للنافبار
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.style.transform = 'translateY(-100%)';
        navbar.style.opacity = '0';
        
        setTimeout(() => {
            navbar.style.transition = 'all 0.6s ease-out';
            navbar.style.transform = 'translateY(0)';
            navbar.style.opacity = '1';
        }, 100);
    }
}

// تأثيرات التمرير المتقدمة
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                element.style.transition = 'all 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                element.style.opacity = '1';
                element.style.transform = 'translateY(0) scale(1)';
                element.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // مراقبة العناصر القابلة للانيميشن
    const animateElements = document.querySelectorAll('.card, .table, .btn-group, .alert');
    animateElements.forEach(element => {
        if (!element.style.opacity) {
            element.style.opacity = '0';
            element.style.transform = 'translateY(30px) scale(0.9)';
            observer.observe(element);
        }
    });
}

// تأثيرات متقدمة جديدة
function initAdvancedAnimations() {
    // تأثير موجي للإحصائيات
    const statCards = document.querySelectorAll('.card.bg-primary, .card.bg-success, .card.bg-info, .card.bg-warning, .card.bg-secondary, .card.bg-danger');
    statCards.forEach((card, index) => {
        // تأثير النبضة للأرقام
        const number = card.querySelector('h3');
        if (number) {
            setTimeout(() => {
                animateCountUp(number);
            }, 800 + (index * 200));
        }
        
        // تأثير الأيقونات
        const icon = card.querySelector('i');
        if (icon) {
            icon.style.transform = 'scale(0) rotate(180deg)';
            icon.style.transition = 'all 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
            
            setTimeout(() => {
                icon.style.transform = 'scale(1) rotate(0deg)';
            }, 600 + (index * 150));
        }
    });
    
    // تأثير النبض للعناصر التفاعلية
    const interactiveElements = document.querySelectorAll('.btn-primary, .btn-success, .btn-info');
    interactiveElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.animation = 'pulse 0.6s ease-in-out';
        });
        
        element.addEventListener('animationend', function() {
            this.style.animation = '';
        });
    });
}

// انيميشن العد التصاعدي
function animateCountUp(element) {
    const finalNumber = parseInt(element.textContent);
    const duration = 2000;
    const startTime = performance.now();
    
    function updateNumber(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // استخدام easing function
        const easeOutCubic = 1 - Math.pow(1 - progress, 3);
        const currentNumber = Math.floor(finalNumber * easeOutCubic);
        
        element.textContent = currentNumber;
        element.style.transform = `scale(${1 + (Math.sin(progress * Math.PI) * 0.1)})`;
        
        if (progress < 1) {
            requestAnimationFrame(updateNumber);
        } else {
            element.style.transform = 'scale(1)';
            // تأثير وميض في النهاية
            element.style.animation = 'flash 0.5s ease-in-out';
        }
    }
    
    requestAnimationFrame(updateNumber);
}

// تأكيد الحذف المطور
function initDeleteConfirmations() {
    const deleteButtons = document.querySelectorAll('a[href*="/delete"], button[data-action="delete"]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const itemName = this.closest('tr')?.children[1]?.textContent || 'هذا العنصر';
            
            // إنشاء modal مخصص للتأكيد
            showCustomConfirm(
                `حذف ${itemName.trim()}`,
                'هل أنت متأكد من حذف هذا العنصر؟ لا يمكن التراجع عن هذا الإجراء.',
                () => {
                    // تأثير انزلاق للصف المحذوف
                    const row = this.closest('tr');
                    if (row) {
                        row.style.transition = 'all 0.5s ease';
                        row.style.transform = 'translateX(100%) scale(0.8)';
                        row.style.opacity = '0';
                        
                        setTimeout(() => {
                            window.location.href = this.href;
                        }, 500);
                    } else {
                        window.location.href = this.href;
                    }
                }
            );
        });
    });
}

// modal التأكيد المخصص
function showCustomConfirm(title, message, onConfirm) {
    const modal = document.createElement('div');
    modal.className = 'custom-confirm-modal';
    modal.innerHTML = `
        <div class="custom-confirm-overlay">
            <div class="custom-confirm-dialog">
                <div class="custom-confirm-header">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h5>${title}</h5>
                </div>
                <div class="custom-confirm-body">
                    <p>${message}</p>
                </div>
                <div class="custom-confirm-footer">
                    <button class="btn btn-secondary cancel-btn">إلغاء</button>
                    <button class="btn btn-danger confirm-btn">تأكيد الحذف</button>
                </div>
            </div>
        </div>
    `;
    
    // إضافة الستايلات
    if (!document.querySelector('#custom-confirm-style')) {
        const style = document.createElement('style');
        style.id = 'custom-confirm-style';
        style.textContent = `
            .custom-confirm-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
            }
            
            .custom-confirm-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                animation: fadeIn 0.3s ease;
            }
            
            .custom-confirm-dialog {
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
                max-width: 400px;
                width: 90%;
                animation: slideUp 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            }
            
            .custom-confirm-header {
                padding: 20px;
                text-align: center;
                border-bottom: 1px solid #eee;
            }
            
            .custom-confirm-header i {
                color: #f39c12;
                font-size: 2rem;
                margin-bottom: 10px;
            }
            
            .custom-confirm-body {
                padding: 20px;
                text-align: center;
                color: #666;
            }
            
            .custom-confirm-footer {
                padding: 20px;
                display: flex;
                gap: 10px;
                justify-content: center;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes slideUp {
                from { transform: translateY(50px) scale(0.9); opacity: 0; }
                to { transform: translateY(0) scale(1); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(modal);
    
    // الأحداث
    modal.querySelector('.cancel-btn').addEventListener('click', () => {
        modal.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => modal.remove(), 300);
    });
    
    modal.querySelector('.confirm-btn').addEventListener('click', () => {
        modal.remove();
        onConfirm();
    });
    
    modal.querySelector('.custom-confirm-overlay').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) {
            modal.remove();
        }
    });
}

// تحسينات واجهة المستخدم المطورة
function initUIEnhancements() {
    // تأثير Ripple للأزرار مع ألوان متنوعة
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            createAdvancedRipple(e, this);
        });
        
        // تأثير الحركة عند التحويم
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // تحسين التنقل في الجداول
    initAdvancedTableEnhancements();
    
    // تحسين القوائم المنسدلة
    initDropdownEnhancements();
    
    // تأثيرات للنافبار
    initNavbarEnhancements();
}

// تأثير Ripple متقدم
function createAdvancedRipple(event, button) {
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    const rect = button.getBoundingClientRect();
    circle.style.width = circle.style.height = diameter + 'px';
    circle.style.left = (event.clientX - rect.left - radius) + 'px';
    circle.style.top = (event.clientY - rect.top - radius) + 'px';
    circle.classList.add('advanced-ripple');
    
    // تحديد لون الـ ripple حسب نوع الزر
    let rippleColor = 'rgba(255, 255, 255, 0.6)';
    if (button.classList.contains('btn-outline-primary')) {
        rippleColor = 'rgba(0, 123, 255, 0.3)';
    } else if (button.classList.contains('btn-outline-success')) {
        rippleColor = 'rgba(40, 167, 69, 0.3)';
    } else if (button.classList.contains('btn-outline-danger')) {
        rippleColor = 'rgba(220, 53, 69, 0.3)';
    }
    
    circle.style.background = rippleColor;
    
    // إضافة الستايلات المطورة
    if (!document.querySelector('#advanced-ripple-style')) {
        const style = document.createElement('style');
        style.id = 'advanced-ripple-style';
        style.textContent = `
            .btn { 
                position: relative; 
                overflow: hidden; 
                transition: all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94);
            }
            
            .advanced-ripple {
                position: absolute;
                border-radius: 50%;
                transform: scale(0);
                animation: advanced-ripple-animation 0.8s cubic-bezier(0.25, 0.46, 0.45, 0.94);
                pointer-events: none;
            }
            
            @keyframes advanced-ripple-animation {
                0% { 
                    transform: scale(0); 
                    opacity: 0.8; 
                }
                50% { 
                    transform: scale(2); 
                    opacity: 0.4; 
                }
                100% { 
                    transform: scale(4); 
                    opacity: 0; 
                }
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            @keyframes flash {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.7; }
            }
        `;
        document.head.appendChild(style);
    }
    
    const existingRipple = button.querySelector('.advanced-ripple');
    if (existingRipple) {
        existingRipple.remove();
    }
    
    button.appendChild(circle);
    
    // إزالة التأثير بعد انتهائه
    setTimeout(() => {
        if (circle.parentNode) {
            circle.remove();
        }
    }, 800);
}

// تحسينات الجداول المتقدمة
function initAdvancedTableEnhancements() {
    const tables = document.querySelectorAll('.table');
    
    tables.forEach(table => {
        // تأثيرات متقدمة للصفوف
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach((row, index) => {
            // انيميشن دخول الصفوف
            row.style.opacity = '0';
            row.style.transform = 'translateX(-20px)';
            row.style.transition = 'all 0.5s ease';
            
            setTimeout(() => {
                row.style.opacity = '1';
                row.style.transform = 'translateX(0)';
            }, index * 100);
            
            // تأثيرات التفاعل
            row.addEventListener('mouseenter', function() {
                this.style.transform = 'translateX(5px) scale(1.02)';
                this.style.boxShadow = '0 5px 15px rgba(0,0,0,0.1)';
                this.style.zIndex = '10';
            });
            
            row.addEventListener('mouseleave', function() {
                this.style.transform = 'translateX(0) scale(1)';
                this.style.boxShadow = 'none';
                this.style.zIndex = '1';
            });
        });
        
        // تحسين رؤوس الجداول
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.style.transform = 'translateY(-20px)';
            header.style.opacity = '0';
            
            setTimeout(() => {
                header.style.transition = 'all 0.5s ease';
                header.style.transform = 'translateY(0)';
                header.style.opacity = '1';
            }, index * 80);
        });
    });
}

// تحسينات النافبار
function initNavbarEnhancements() {
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        // تأثير التمرير
        link.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.05)';
        });
        
        link.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
        
        // تأثير النقر
        link.addEventListener('click', function() {
            this.style.animation = 'pulse 0.3s ease';
        });
    });
    
    // تأثير العلامة التجارية
    const brand = document.querySelector('.navbar-brand');
    if (brand) {
        brand.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.1) rotate(2deg)';
        });
        
        brand.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1) rotate(0deg)';
        });
    }
}

// باقي الدوال كما هي مع تحسينات طفيفة...
function autoHideAlerts() {
    const alerts = document.querySelectorAll('.alert');
    
    alerts.forEach((alert, index) => {
        // انيميشن دخول
        alert.style.transform = 'translateY(-20px) scale(0.9)';
        alert.style.opacity = '0';
        
        setTimeout(() => {
            alert.style.transition = 'all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            alert.style.transform = 'translateY(0) scale(1)';
            alert.style.opacity = '1';
        }, index * 200);
        
        // إضافة زر الإغلاق إذا لم يكن موجوداً
        if (!alert.querySelector('.btn-close')) {
            const closeBtn = document.createElement('button');
            closeBtn.className = 'btn-close';
            closeBtn.setAttribute('data-bs-dismiss', 'alert');
            alert.appendChild(closeBtn);
        }
        
        // إخفاء تلقائي بعد 5 ثوانِ مع انيميشن خروج
        setTimeout(() => {
            if (alert.parentNode) {
                alert.style.transition = 'all 0.5s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateX(100%) scale(0.8)';
                
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.remove();
                    }
                }, 500);
            }
        }, 5000);
    });
}

// تحسينات النماذج المطورة
function initFormEnhancements() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        // تأثيرات للحقول
        inputs.forEach(input => {
            // تأثير التركيز
            input.addEventListener('focus', function() {
                this.parentElement.style.transform = 'scale(1.02)';
                this.style.boxShadow = '0 0 20px rgba(52, 152, 219, 0.3)';
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.style.transform = 'scale(1)';
                this.style.boxShadow = 'none';
            });
            
            // إزالة رسائل الخطأ مع انيميشن
            input.addEventListener('input', function() {
                if (this.classList.contains('is-invalid')) {
                    this.style.transition = 'all 0.3s ease';
                    this.classList.remove('is-invalid');
                }
            });
        });
        
        // التحقق المطور من البيانات
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    field.style.animation = 'shake 0.5s ease-in-out';
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showEnhancedNotification('يرجى ملء جميع الحقول المطلوبة', 'error');
            }
        });
    });
}

// باقي الدوال...
function initDropdownEnhancements() {
    const dropdowns = document.querySelectorAll('.dropdown-menu');
    
    dropdowns.forEach(dropdown => {
        dropdown.addEventListener('show.bs.dropdown', function() {
            this.style.opacity = '0';
            this.style.transform = 'translateY(-15px) scale(0.9)';
            
            setTimeout(() => {
                this.style.transition = 'all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
                this.style.opacity = '1';
                this.style.transform = 'translateY(0) scale(1)';
            }, 50);
        });
    });
}

// إشعارات محسنة
function showEnhancedNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} enhanced-notification`;
    notification.innerHTML = `
        <i class="fas fa-${getIconForType(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.25);
        border-radius: 12px;
        transform: translateX(120%) scale(0.8);
        transition: all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(0) scale(1)';
    }, 100);
    
    setTimeout(() => {
        notification.style.transform = 'translateX(120%) scale(0.8)';
        setTimeout(() => notification.remove(), 400);
    }, 4500);
}

function getIconForType(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// إضافة انيميشن الاهتزاز للأخطاء
if (!document.querySelector('#shake-animation')) {
    const shakeStyle = document.createElement('style');
    shakeStyle.id = 'shake-animation';
    shakeStyle.textContent = `
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-5px); }
            75% { transform: translateX(5px); }
        }
        
        @keyframes fadeOut {
            from { opacity: 1; transform: scale(1); }
            to { opacity: 0; transform: scale(0.9); }
        }
    `;
    document.head.appendChild(shakeStyle);
}