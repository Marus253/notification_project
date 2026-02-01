"""
Application Flask du système de notification
Utilise TES classes core/
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import json
from datetime import datetime

# Importe TES classes
from core.alert_types import SecurityAlert, WeatherAlert, HealthAlert, AcademicAlert
from core.notifiers import EmergencyNotifier
from core.advanced import NotificationMeta, UserNotification

app = Flask(__name__)
app.secret_key = 'secret-key-123'  # Pour les messages flash

# Données en mémoire (pour la simplicité)
notifications_history = []
users = {
    'admin': {'password': 'admin123', 'name': 'Administrateur'},
    'etudiant': {'password': 'etu123', 'name': 'Étudiant Test'}
}

# Page d'accueil
@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html', 
                         notifications=notifications_history[-5:],  # 5 dernières
                         total=len(notifications_history))

# Page d'envoi
@app.route('/send', methods=['GET', 'POST'])
def send_notification():
    """Envoyer une notification"""
    
    if request.method == 'POST':
        alert_type = request.form.get('alert_type')
        message = request.form.get('message')
        
        if not message:
            flash('Veuillez entrer un message', 'danger')
            return redirect('/send')
        
        print(f"\n{'='*50}")
        print(f"📨 NOUVELLE NOTIFICATION")
        print(f"Type: {alert_type}")
        print(f"Message: {message}")
        print('='*50)
        
        result = ""
        
        try:
            # Utilise TES classes
            if alert_type == 'SECURITY':
                alert = SecurityAlert(message)
                result = alert.send()
                priority = "URGENT"
                icon = "🚨"
                
            elif alert_type == 'WEATHER':
                alert = WeatherAlert(message)
                result = alert.send()
                priority = "MEDIUM"
                icon = "🌧️"
                
            elif alert_type == 'HEALTH':
                alert = HealthAlert(message)
                result = alert.send()
                priority = "HIGH"
                icon = "🏥"
                
            elif alert_type == 'ACADEMIC':
                alert = AcademicAlert(message)
                result = alert.send()
                priority = "LOW"
                icon = "📚"
                
            else:
                flash('Type d\'alerte invalide', 'danger')
                return redirect('/send')
            
            # Sauvegarde dans l'historique
            notifications_history.append({
                'type': alert_type,
                'message': message,
                'priority': priority,
                'icon': icon,
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'result': result
            })
            
            flash(f'{icon} Notification envoyée avec succès!', 'success')
            
        except Exception as e:
            flash(f'Erreur: {str(e)}', 'danger')
            result = f"Erreur: {str(e)}"
        
        return render_template('send.html', result=result)
    
    return render_template('send.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    """Dashboard avec statistiques"""
    
    # Calcule les statistiques
    stats = {
        'total': len(notifications_history),
        'security': sum(1 for n in notifications_history if n['type'] == 'SECURITY'),
        'weather': sum(1 for n in notifications_history if n['type'] == 'WEATHER'),
        'health': sum(1 for n in notifications_history if n['type'] == 'HEALTH'),
        'academic': sum(1 for n in notifications_history if n['type'] == 'ACADEMIC'),
        'urgent': sum(1 for n in notifications_history if n['priority'] == 'URGENT'),
        'high': sum(1 for n in notifications_history if n['priority'] == 'HIGH'),
        'medium': sum(1 for n in notifications_history if n['priority'] == 'MEDIUM'),
        'low': sum(1 for n in notifications_history if n['priority'] == 'LOW'),
    }
    
    # Récupère le MRO pour la démo
    mro_list = []
    try:
        for i, cls in enumerate(EmergencyNotifier.__mro__):
            mro_list.append(str(cls))
    except:
        mro_list = ["MRO non disponible"]
    
    return render_template('dashboard.html', 
                         stats=stats,
                         mro=mro_list,
                         notifications=notifications_history[-10:])

# Page de démonstration POO
@app.route('/demo-poo')
def demo_poo():
    """Page de démonstration des concepts POO"""
    
    results = {}
    
    # 1. Test des mixins
    from core.mixins import SMSMixin, EmailMixin
    class TestMixin(SMSMixin, EmailMixin):
        pass
    test_mixin = TestMixin()
    results['mixins'] = " Mixins SMS et Email fonctionnels"
    
    # 2. Test du MRO
    from core.notifiers import EmergencyNotifier
    mro_info = EmergencyNotifier("Test").display_mro()
    results['mro'] = f" MRO avec {len(mro_info)} classes"
    
    # 3. Test des décorateurs
    from core.decorators import log_notification
    @log_notification
    def test_func():
        return "Décorateur fonctionnel"
    results['decorators'] = test_func()
    
    # 4. Test des descripteurs
    try:
        notif = UserNotification("Test", priority="HIGH", email="test@campus.edu")
        results['descripteurs'] = f" {notif}"
    except Exception as e:
        results['descripteurs'] = f" {e}"
    
    # 5. Test de la métaclasse
    from core.advanced import NotificationMeta
    registry = NotificationMeta.get_registered_classes()
    results['metaclasse'] = f" {len(registry)} classes enregistrées"
    
    # 6. Test des alertes
    security = SecurityAlert("Test sécurité")
    weather = WeatherAlert("Test météo")
    results['alertes'] = f" Alertes: {security.priority}, {weather.priority}"
    
    return render_template('demo_poo.html', results=results)

# API simple
@app.route('/api/send', methods=['POST'])
def api_send():
    """API pour envoyer des notifications (JSON)"""
    try:
        data = request.get_json()
        alert_type = data.get('type')
        message = data.get('message')
        
        if not alert_type or not message:
            return jsonify({'error': 'Type et message requis'}), 400
        
        # Utilise TES classes
        if alert_type == 'SECURITY':
            alert = SecurityAlert(message)
            result = alert.send()
        elif alert_type == 'WEATHER':
            alert = WeatherAlert(message)
            result = alert.send()
        else:
            return jsonify({'error': 'Type non supporté'}), 400
        
        return jsonify({
            'status': 'success',
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Page de connexion simple
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion simplifiée"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in users and users[username]['password'] == password:
            flash(f'Bienvenue {users[username]["name"]}!', 'success')
            return redirect('/')
        else:
            flash('Identifiants incorrects', 'danger')
    
    return render_template('login.html')

# Page 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    print(" Lancement de l'application Flask...")
    print(" Classes POO chargées:")
    print("   - SMSMixin, EmailMixin, PushMixin")
    print("   - SecurityAlert, WeatherAlert, HealthAlert, AcademicAlert")
    print("   - EmergencyNotifier (MRO)")
    print("   - Descripteurs et Métaclasse")
    print("\n Serveur démarré sur http://localhost:5000")
    app.run(debug=True, port=5000)