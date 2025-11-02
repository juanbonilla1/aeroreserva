// AeroReserva - JavaScript corregido
console.log("✈️ AeroReserva - Frontend funcionando");

document.addEventListener('DOMContentLoaded', function() {
    console.log("✅ DOM cargado correctamente");
    
    // Inicializar funcionalidades
    initFlightCards();
    initBookingForms();
});

function initFlightCards() {
    const cards = document.querySelectorAll('.flight-card');
    console.log(`🎫 Encontradas ${cards.length} cards de vuelo`);
    
    cards.forEach((card, index) => {
        // Animación escalonada
        card.style.animationDelay = `${index * 0.1}s`;
        
        // Efectos hover
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

function initBookingForms() {
    const forms = document.querySelectorAll('.booking-form');
    
    forms.forEach(form => {
        const passengerInput = form.querySelector('input[name="num_pasajeros"]');
        const priceElement = form.closest('.price-section').querySelector('.price');
        
        if (passengerInput && priceElement) {
            const basePrice = parseInt(priceElement.textContent.replace('$', ''));
            
            passengerInput.addEventListener('input', function() {
                const passengers = parseInt(this.value) || 1;
                const total = basePrice * passengers;
                
                // Efecto visual
                priceElement.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    priceElement.style.transform = 'scale(1)';
                }, 150);
            });
        }
        
        // Manejar envío del formulario
        form.addEventListener('submit', function(e) {
            const button = this.querySelector('button[type="submit"]');
            if (button) {
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
                button.disabled = true;
            }
        });
    });
}

// Mostrar notificaciones
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 90px; right: 20px; z-index: 1060; min-width: 300px;';
    
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle', 
        'info': 'info-circle',
        'warning': 'exclamation-circle'
    };
    
    notification.innerHTML = `
        <i class="fas fa-${icons[type] || 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}
