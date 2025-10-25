from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

# 🚨 CONFIGURACIÓN PARA RENDER.COM
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///school_management.db').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mi_pequeño_universo_secret_key')

CORS(app)
db = SQLAlchemy(app)

# 🚨 MIDDLEWARE DE SEGURIDAD
@app.before_request
def check_auth():
    if not request.endpoint or request.endpoint in ['login_page', 'login', 'static', 'logout']:
        return
    if not session.get('logged_in'):
        return redirect('/')

# === TODOS TUS MODELOS (EXACTAMENTE IGUAL) ===
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='admin')
    full_name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)

class SchoolYear(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(20), nullable=False, unique=True)
    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='active')

class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age_range = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    current_students = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')

class PaymentConcept(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    frequency = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Información Personal
    last_name = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    birth_date = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    nationality = db.Column(db.String(50), default='Peruana')
    
    # Información de Contacto
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    photo = db.Column(db.String(200))
    
    # Información del Padre
    father_names = db.Column(db.String(100))
    father_dni = db.Column(db.String(20))
    father_birth_date = db.Column(db.String(50))
    father_phone = db.Column(db.String(20))
    father_email = db.Column(db.String(100))
    father_occupation = db.Column(db.String(100))
    
    # Información de la Madre
    mother_names = db.Column(db.String(100))
    mother_dni = db.Column(db.String(20))
    mother_birth_date = db.Column(db.String(50))
    mother_phone = db.Column(db.String(20))
    mother_email = db.Column(db.String(100))
    mother_occupation = db.Column(db.String(100))
    
    # Contacto de Emergencia
    emergency_contact = db.Column(db.String(100))
    emergency_relationship = db.Column(db.String(50))
    emergency_phone = db.Column(db.String(20))
    emergency_address = db.Column(db.Text)
    
    # Datos Médicos
    blood_type = db.Column(db.String(10))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    allergies = db.Column(db.Text)
    medications = db.Column(db.Text)
    medical_conditions = db.Column(db.Text)
    activity_restrictions = db.Column(db.Text)
    vaccines_up_to_date = db.Column(db.Boolean, default=True)
    medical_observations = db.Column(db.Text)
    
    status = db.Column(db.String(20), default='active')
    enrollment_date = db.Column(db.String(50), default=lambda: datetime.now().isoformat())

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    enrollment_date = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    status = db.Column(db.String(20), default='active')
   
    student = db.relationship('Student', backref=db.backref('enrollments', lazy=True))
    classroom = db.relationship('Classroom', backref=db.backref('enrollments', lazy=True))

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    concept_id = db.Column(db.Integer, db.ForeignKey('payment_concept.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.String(50), nullable=False)
    due_date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pagado')
    receipt_number = db.Column(db.String(50), unique=True)
    
    student = db.relationship('Student', backref=db.backref('payments', lazy=True))
    concept = db.relationship('PaymentConcept', backref=db.backref('payments', lazy=True))

class PaymentPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    concept_id = db.Column(db.Integer, db.ForeignKey('payment_concept.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    installments = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='active')
    created_date = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    
    student = db.relationship('Student')
    concept = db.relationship('PaymentConcept')

class PaymentInstallment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('payment_plan.id'), nullable=False)
    installment_number = db.Column(db.Integer, nullable=False)
    due_date = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    payment_date = db.Column(db.String(50))
    payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
    
    plan = db.relationship('PaymentPlan')
    payment = db.relationship('Payment')

class AlmacenUtil(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aula_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    material = db.Column(db.String(200), nullable=False)
    cantidad_requerida = db.Column(db.Integer, nullable=False)
    especificaciones = db.Column(db.Text)
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    
    aula = db.relationship('Classroom', backref=db.backref('utiles', lazy=True))

class AlmacenEntrega(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    util_id = db.Column(db.Integer, db.ForeignKey('almacen_util.id'), nullable=False)
    cantidad_entregada = db.Column(db.Integer, nullable=False)
    fecha_entrega = db.Column(db.String(50))
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    
    estudiante = db.relationship('Student', backref=db.backref('entregas_utiles', lazy=True))
    util = db.relationship('AlmacenUtil', backref=db.backref('entregas', lazy=True))

class MaterialAula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    stock_actual = db.Column(db.Integer, default=0)
    stock_minimo = db.Column(db.Integer, default=0)
    unidad_medida = db.Column(db.String(50), default='unidades')
    ubicacion = db.Column(db.String(100))
    proveedor = db.Column(db.String(100))
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())

class MovimientoMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('material_aula.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(200), nullable=False)
    observaciones = db.Column(db.Text)
    fecha_movimiento = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    responsable = db.Column(db.String(100))
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    
    material = db.relationship('MaterialAula', backref=db.backref('movimientos', lazy=True))

class BienAula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo_patrimonial = db.Column(db.String(100), unique=True)
    nombre = db.Column(db.String(200), nullable=False)
    categoria = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    marca = db.Column(db.String(100))
    modelo = db.Column(db.String(100))
    numero_serie = db.Column(db.String(100))
    estado = db.Column(db.String(50), default='bueno')
    ubicacion = db.Column(db.String(100))
    aula_id = db.Column(db.Integer, db.ForeignKey('classroom.id'))
    fecha_adquisicion = db.Column(db.String(50))
    valor_adquisicion = db.Column(db.Float)
    proveedor = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    
    aula = db.relationship('Classroom', backref=db.backref('bienes', lazy=True))

class MantenimientoBien(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bien_id = db.Column(db.Integer, db.ForeignKey('bien_aula.id'), nullable=False)
    tipo_mantenimiento = db.Column(db.String(50), nullable=False)
    fecha_mantenimiento = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    costo = db.Column(db.Float, default=0)
    proveedor_mantenimiento = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.String(50), default=lambda: datetime.now().isoformat())
    
    bien = db.relationship('BienAula', backref=db.backref('mantenimientos', lazy=True))

# === TODAS TUS RUTAS (EXACTAMENTE IGUAL) ===
@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('dashboard.html')

@app.route('/config-año')
def config_ano():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('config-año.html')

@app.route('/config-aulas')
def config_aulas():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('config-aulas.html')

@app.route('/config-conceptos')
def config_conceptos():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('config-conceptos.html')

@app.route('/estudiantes')
def estudiantes():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('estudiantes.html')

@app.route('/matriculas')
def matriculas():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('matriculas.html')

@app.route('/certificado-matricula')
def certificate_page():
    return render_template('certificado_matricula.html')

@app.route('/api/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/pagos')
def pagos():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('pagos.html')

@app.route('/planes-pago')
def planes_pago():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('planes-pago.html')

@app.route('/cronograma-pagos')
def cronograma_pagos():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('cronograma-pagos.html')

@app.route('/almacen')
def almacen():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('almacen.html')

@app.route('/reportes')
def reportes():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('reportes.html')

@app.route('/comprobante-pago')
def comprobante_page():
    return render_template('comprobante-pago.html')

# === TODAS TUS APIs (EXACTAMENTE IGUAL) ===
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    user = User.query.filter_by(username=username, is_active=True).first()
    
    if user and check_password_hash(user.password, password):
        session['logged_in'] = True
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        session['full_name'] = user.full_name or username
        
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Usuario o contraseña incorrectos'})

# ... (TODAS TUS DEMÁS APIs EXACTAMENTE IGUALES - las copias de tu archivo original)

# === FUNCIONES AUXILIARES ===
def calculate_age(birth_date):
    if not birth_date:
        return 0
    try:
        birth = datetime.strptime(birth_date, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return age
    except:
        return 0

def create_superadmin():
    if User.query.count() == 0:
        superadmin = User(
            username='admin',
            password=generate_password_hash('R@nny1511'),
            role='superadmin', 
            full_name='Administrador Principal'
        )
        db.session.add(superadmin)
        db.session.commit()
        print("✅ Superadmin creado: usuario=admin, contraseña=R@nny1511")

def init_database():
    with app.app_context():
        db.create_all()
        create_superadmin()
        print("✅ Base de datos lista - Los datos son PERMANENTES")

# === INICIO PARA PRODUCCIÓN ===
if __name__ == '__main__':
    init_database()
    port = int(os.environ.get('PORT', 5000))

    app.run(host='0.0.0.0', port=port)
