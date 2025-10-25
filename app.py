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
# APIS PARA CONFIGURACIÓN
@app.route('/api/school-years', methods=['GET', 'POST'])
def school_years():
    if request.method == 'GET':
        years = SchoolYear.query.all()
        return jsonify([{
            'id': y.id, 'year': y.year, 
            'start_date': y.start_date, 'end_date': y.end_date
        } for y in years])
    
    elif request.method == 'POST':
        data = request.get_json()
        year = SchoolYear(
            year=data['year'],
            start_date=data['start_date'],
            end_date=data['end_date']
        )
        db.session.add(year)
        db.session.commit()
        return jsonify({'success': True})

@app.route('/api/classrooms', methods=['GET', 'POST'])
def classrooms():
    if request.method == 'GET':
        classrooms = Classroom.query.all()
        return jsonify([{
            'id': c.id, 'name': c.name, 'age_range': c.age_range,
            'capacity': c.capacity, 'current_students': c.current_students
        } for c in classrooms])
    
    elif request.method == 'POST':
        data = request.get_json()
        classroom = Classroom(
            name=data['name'],
            age_range=data['age_range'],
            capacity=data['capacity']
        )
        db.session.add(classroom)
        db.session.commit()
        return jsonify({'success': True})

@app.route('/api/payment-concepts', methods=['GET', 'POST'])
def payment_concepts():
    if request.method == 'GET':
        concepts = PaymentConcept.query.all()
        return jsonify([{
            'id': c.id, 'name': c.name, 'description': c.description,
            'amount': c.amount, 'frequency': c.frequency
        } for c in concepts])
    
    elif request.method == 'POST':
        data = request.get_json()
        concept = PaymentConcept(
            name=data['name'],
            description=data.get('description', ''),
            amount=data['amount'],
            frequency=data.get('frequency', 'mensual')
        )
        db.session.add(concept)
        db.session.commit()
        return jsonify({'success': True})

# APIS PARA ESTUDIANTES - CORREGIDAS
@app.route('/api/students', methods=['GET', 'POST', 'PUT'])
def students():
    try:
        if request.method == 'GET':
            students = Student.query.all()
            return jsonify([{
                'id': s.id,
                'first_name': s.first_name,
                'last_name': s.last_name,
                'dni': s.dni,
                'birth_date': s.birth_date,
                'age': calculate_age(s.birth_date),
                'gender': s.gender,
                'phone': s.phone,
                'status': s.status
            } for s in students])
        
        elif request.method == 'POST':
            data = request.get_json()
            print("Datos recibidos para nuevo estudiante:", data)  # DEBUG
            
            # Validar campos requeridos
            required_fields = ['last_name', 'first_name', 'dni', 'birth_date', 'gender', 'address', 'phone']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'success': False, 'error': f'Campo requerido faltante: {field}'}), 400
            
            # Verificar si DNI ya existe
            existing_student = Student.query.filter_by(dni=data['dni']).first()
            if existing_student:
                return jsonify({'success': False, 'error': 'El DNI ya está registrado'}), 400
            
            # Convertir valores numéricos
            height = data.get('height')
            weight = data.get('weight')
            
            if height:
                try:
                    height = float(height)
                except (ValueError, TypeError):
                    height = None
            
            if weight:
                try:
                    weight = float(weight)
                except (ValueError, TypeError):
                    weight = None
            
            student = Student(
                # Información Personal
                last_name=data['last_name'],
                first_name=data['first_name'],
                dni=data['dni'],
                birth_date=data['birth_date'],
                gender=data['gender'],
                nationality=data.get('nationality', 'Peruana'),
                
                # Información de Contacto
                address=data['address'],
                phone=data['phone'],
                email=data.get('email', ''),
                
                # Información del Padre
                father_names=data.get('father_names', ''),
                father_dni=data.get('father_dni', ''),
                father_birth_date=data.get('father_birth_date', ''),
                father_phone=data.get('father_phone', ''),
                father_email=data.get('father_email', ''),
                father_occupation=data.get('father_occupation', ''),
                
                # Información de la Madre
                mother_names=data.get('mother_names', ''),
                mother_dni=data.get('mother_dni', ''),
                mother_birth_date=data.get('mother_birth_date', ''),
                mother_phone=data.get('mother_phone', ''),
                mother_email=data.get('mother_email', ''),
                mother_occupation=data.get('mother_occupation', ''),
                
                # Contacto de Emergencia
                emergency_contact=data.get('emergency_contact', ''),
                emergency_relationship=data.get('emergency_relationship', ''),
                emergency_phone=data.get('emergency_phone', ''),
                emergency_address=data.get('emergency_address', ''),
                
                # Datos Médicos
                blood_type=data.get('blood_type', ''),
                height=height,
                weight=weight,
                allergies=data.get('allergies', ''),
                medications=data.get('medications', ''),
                medical_conditions=data.get('medical_conditions', ''),
                activity_restrictions=data.get('activity_restrictions', ''),
                vaccines_up_to_date=data.get('vaccines_up_to_date', True),
                medical_observations=data.get('medical_observations', '')
            )
            
            db.session.add(student)
            db.session.commit()
            print(f"✅ Estudiante creado exitosamente: {student.first_name} {student.last_name}")  # DEBUG
            return jsonify({'success': True, 'student_id': student.id})
        
        elif request.method == 'PUT':
            data = request.get_json()
            student_id = data.get('id')
            
            if not student_id:
                return jsonify({'success': False, 'error': 'ID de estudiante requerido'}), 400
            
            student = Student.query.get(student_id)
            if not student:
                return jsonify({'success': False, 'error': 'Estudiante no encontrado'}), 404
            
            # Actualizar campos
            updatable_fields = [
                'last_name', 'first_name', 'dni', 'birth_date', 'gender', 'nationality',
                'address', 'phone', 'email', 'father_names', 'father_dni', 'father_birth_date',
                'father_phone', 'father_email', 'father_occupation', 'mother_names', 'mother_dni',
                'mother_birth_date', 'mother_phone', 'mother_email', 'mother_occupation',
                'emergency_contact', 'emergency_relationship', 'emergency_phone', 'emergency_address',
                'blood_type', 'height', 'weight', 'allergies', 'medications', 'medical_conditions',
                'activity_restrictions', 'vaccines_up_to_date', 'medical_observations', 'status'
            ]
            
            for field in updatable_fields:
                if field in data:
                    setattr(student, field, data[field])
            
            db.session.commit()
            return jsonify({'success': True})
            
    except Exception as e:
        print("Error en /api/students:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

# API para obtener estudiante por ID
@app.route('/api/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    try:
        student = Student.query.get(student_id)
        if not student:
            return jsonify({'success': False, 'error': 'Estudiante no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'student': {
                'id': student.id,
                'last_name': student.last_name,
                'first_name': student.first_name,
                'dni': student.dni,
                'birth_date': student.birth_date,
                'gender': student.gender,
                'nationality': student.nationality,
                'address': student.address,
                'phone': student.phone,
                'email': student.email,
                'father_names': student.father_names,
                'father_dni': student.father_dni,
                'father_birth_date': student.father_birth_date,
                'father_phone': student.father_phone,
                'father_email': student.father_email,
                'father_occupation': student.father_occupation,
                'mother_names': student.mother_names,
                'mother_dni': student.mother_dni,
                'mother_birth_date': student.mother_birth_date,
                'mother_phone': student.mother_phone,
                'mother_email': student.mother_email,
                'mother_occupation': student.mother_occupation,
                'emergency_contact': student.emergency_contact,
                'emergency_relationship': student.emergency_relationship,
                'emergency_phone': student.emergency_phone,
                'emergency_address': student.emergency_address,
                'blood_type': student.blood_type,
                'height': student.height,
                'weight': student.weight,
                'allergies': student.allergies,
                'medications': student.medications,
                'medical_conditions': student.medical_conditions,
                'activity_restrictions': student.activity_restrictions,
                'vaccines_up_to_date': student.vaccines_up_to_date,
                'medical_observations': student.medical_observations,
                'status': student.status,
                'enrollment_date': student.enrollment_date
            }
        })
        
    except Exception as e:
        print("Error en /api/students/<id>:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

# API PARA DASHBOARD
@app.route('/api/dashboard-stats')
def dashboard_stats():
    total_years = SchoolYear.query.count()
    total_classrooms = Classroom.query.count()
    total_concepts = PaymentConcept.query.count()
    total_students = Student.query.count()
    
    return jsonify({
        'school_years': total_years,
        'classrooms': total_classrooms,
        'payment_concepts': total_concepts,
        'students': total_students,
        'setup_complete': total_years > 0 and total_classrooms > 0 and total_concepts > 0
    })

# APIS PARA MATRÍCULAS
@app.route('/api/enrollments', methods=['GET', 'POST'])
def enrollments():
    if request.method == 'GET':
        enrollments = Enrollment.query.options(
            db.joinedload(Enrollment.student),
            db.joinedload(Enrollment.classroom)
        ).all()
        
        return jsonify([{
            'id': e.id,
            'student_id': e.student_id,
            'student_name': f"{e.student.first_name} {e.student.last_name}",
            'student_dni': e.student.dni,
            'classroom_id': e.classroom_id,
            'classroom_name': e.classroom.name,
            'enrollment_date': e.enrollment_date,
            'status': e.status
        } for e in enrollments])
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            print("📅 FECHA RECIBIDA DEL FRONTEND:", data.get('enrollment_date'))  # ← DEBUG
            print("📅 FECHA ACTUAL DEL SERVIDOR:", datetime.now().date().isoformat())  # ← DEBUG
            # Verificar si el estudiante ya está matriculado
            existing_enrollment = Enrollment.query.filter_by(
                student_id=data['student_id'], 
                status='active'
            ).first()
            
            if existing_enrollment:
                return jsonify({'success': False, 'error': 'El estudiante ya está matriculado'})
            
            # Verificar capacidad del aula
            classroom = Classroom.query.get(data['classroom_id'])
            current_enrollments = Enrollment.query.filter_by(
                classroom_id=data['classroom_id'], 
                status='active'
            ).count()
            
            if current_enrollments >= classroom.capacity:
                return jsonify({'success': False, 'error': 'El aula no tiene cupos disponibles'})
            
            enrollment = Enrollment(
                student_id=data['student_id'],
                classroom_id=data['classroom_id'],
                enrollment_date=data.get('enrollment_date')
            )
            
            db.session.add(enrollment)
            db.session.commit()
            print("📅 FECHA GUARDADA EN BD:", enrollment.enrollment_date)  # ← DEBUG
            return jsonify({'success': True, 'enrollment_id': enrollment.id})
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

# API PARA GENERAR CONSTANCIA DE MATRÍCULA
@app.route('/api/enrollments/<int:enrollment_id>/certificate')
def generate_certificate(enrollment_id):
    try:
        enrollment = Enrollment.query.options(
            db.joinedload(Enrollment.student),
            db.joinedload(Enrollment.classroom)
        ).get(enrollment_id)
        
        if not enrollment:
            return jsonify({'success': False, 'error': 'Matrícula no encontrada'}), 404
        
        # Formatear fecha de matrícula
        try:
            enrollment_date = datetime.strptime(enrollment.enrollment_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            enrollment_date = enrollment.enrollment_date
            
        try:
            birth_date = datetime.strptime(enrollment.student.birth_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        except:
            birth_date = enrollment.student.birth_date
        
        # Datos para la constancia
        certificate_data = {
            'enrollment_id': enrollment.id,
            'student_name': f"{enrollment.student.first_name} {enrollment.student.last_name}",
            'student_dni': enrollment.student.dni,
            'student_birth_date': birth_date,
            'classroom_name': enrollment.classroom.name,
            'classroom_age_range': enrollment.classroom.age_range,
            'enrollment_date': enrollment_date,
            'current_date': datetime.now().strftime('%d/%m/%Y'),
            'current_year': datetime.now().year
        }
        
        return jsonify({
            'success': True, 
            'certificate': certificate_data
        })
        
    except Exception as e:
        print("Error generando certificado:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

# API para estudiantes no matriculados
@app.route('/api/students/unenrolled')
def unenrolled_students():
    try:
        # Estudiantes que no tienen matrículas activas
        enrolled_student_ids = db.session.query(Enrollment.student_id).filter_by(status='active')
        unenrolled_students = Student.query.filter(
            Student.status == 'active',
            ~Student.id.in_(enrolled_student_ids)
        ).all()
        
        return jsonify([{
            'id': s.id,
            'first_name': s.first_name,
            'last_name': s.last_name,
            'dni': s.dni,
            'birth_date': s.birth_date,
            'age': calculate_age(s.birth_date)
        } for s in unenrolled_students])
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API para aulas disponibles
@app.route('/api/classrooms/available')
def available_classrooms():
    try:
        classrooms = Classroom.query.filter_by(status='active').all()
        
        result = []
        for classroom in classrooms:
            current_enrollments = Enrollment.query.filter_by(
                classroom_id=classroom.id, 
                status='active'
            ).count()
            
            result.append({
                'id': classroom.id,
                'name': classroom.name,
                'age_range': classroom.age_range,
                'capacity': classroom.capacity,
                'current_enrollments': current_enrollments,
                'available_spots': classroom.capacity - current_enrollments
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# API PARA ESTUDIANTES MATRICULADOS
@app.route('/api/students/enrolled')
def enrolled_students():
    try:
        # Obtener matrículas activas
        enrollments = Enrollment.query.filter_by(status='active').all()
        
        result = []
        for enrollment in enrollments:
            student = enrollment.student
            result.append({
                'id': student.id,
                'name': f"{student.first_name} {student.last_name}",
                'dni': student.dni,
                'classroom': enrollment.classroom.name
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# APIS PARA MATRÍCULAS - AGREGAR DESPUÉS DE LAS APIS EXISTENTES DE ENROLLMENTS

# Ver detalles de matrícula
@app.route('/api/enrollments/<int:enrollment_id>/details')
def get_enrollment_details(enrollment_id):
    """API para el botón VER matrícula"""
    try:
        enrollment = Enrollment.query.options(
            db.joinedload(Enrollment.student),
            db.joinedload(Enrollment.classroom)
        ).get(enrollment_id)
        
        if not enrollment:
            return jsonify({'success': False, 'error': 'Matrícula no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'enrollment': {
                'id': enrollment.id,
                'student_name': f"{enrollment.student.first_name} {enrollment.student.last_name}",
                'student_dni': enrollment.student.dni,
                'classroom_name': enrollment.classroom.name,
                'classroom_id': enrollment.classroom_id,
                'enrollment_date': enrollment.enrollment_date,
                'status': enrollment.status
            }
        })
        
    except Exception as e:
        print("Error en get_enrollment_details:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

# Obtener matrícula para editar
@app.route('/api/enrollments/<int:enrollment_id>/edit')
def get_enrollment_for_edit(enrollment_id):
    """API para el botón EDITAR matrícula"""
    try:
        enrollment = Enrollment.query.options(
            db.joinedload(Enrollment.student),
            db.joinedload(Enrollment.classroom)
        ).get(enrollment_id)
        
        if not enrollment:
            return jsonify({'success': False, 'error': 'Matrícula no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'enrollment': {
                'id': enrollment.id,
                'student_id': enrollment.student_id,
                'student_name': f"{enrollment.student.first_name} {enrollment.student.last_name}",
                'classroom_id': enrollment.classroom_id,
                'classroom_name': enrollment.classroom.name,
                'enrollment_date': enrollment.enrollment_date,
                'status': enrollment.status
            }
        })
        
    except Exception as e:
        print("Error en get_enrollment_for_edit:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

# Actualizar matrícula
@app.route('/api/enrollments/<int:enrollment_id>/update', methods=['PUT'])
def update_enrollment(enrollment_id):
    """API para actualizar matrícula (cambiar aula/fecha)"""
    try:
        data = request.get_json()
        enrollment = Enrollment.query.get(enrollment_id)
        
        if not enrollment:
            return jsonify({'success': False, 'error': 'Matrícula no encontrada'}), 404
        
        # Validar que el nuevo aula existe
        new_classroom = Classroom.query.get(data['classroom_id'])
        if not new_classroom:
            return jsonify({'success': False, 'error': 'Aula no encontrada'}), 404
        
        # Si se cambia de aula, verificar capacidad
        if enrollment.classroom_id != data['classroom_id']:
            current_enrollments = Enrollment.query.filter_by(
                classroom_id=data['classroom_id'], 
                status='active'
            ).count()
            
            if current_enrollments >= new_classroom.capacity:
                return jsonify({'success': False, 'error': 'El aula no tiene cupos disponibles'}), 400
        
        # Actualizar campos
        enrollment.classroom_id = data['classroom_id']
        enrollment.enrollment_date = data['enrollment_date']
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Matrícula actualizada correctamente'})
        
    except Exception as e:
        db.session.rollback()
        print("Error en update_enrollment:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

# Anular matrícula
@app.route('/api/enrollments/<int:enrollment_id>/cancel', methods=['PUT'])
def cancel_enrollment(enrollment_id):
    """API para anular matrícula (cambiar estado a inactive)"""
    try:
        enrollment = Enrollment.query.get(enrollment_id)
        
        if not enrollment:
            return jsonify({'success': False, 'error': 'Matrícula no encontrada'}), 404
        
        # Cambiar estado a inactivo
        enrollment.status = 'inactive'
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Matrícula anulada correctamente'})
        
    except Exception as e:
        db.session.rollback()
        print("Error en cancel_enrollment:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

# API PARA PAGOS
@app.route('/api/payments', methods=['GET', 'POST'])
def payments():
    if request.method == 'GET':
        payments = Payment.query.options(
            db.joinedload(Payment.student),
            db.joinedload(Payment.concept)
        ).all()
        
        return jsonify([{
            'id': p.id,
            'student_name': f"{p.student.first_name} {p.student.last_name}",
            'student_dni': p.student.dni,
            'concept_name': p.concept.name,
            'amount': p.amount,
            'payment_date': p.payment_date,
            'due_date': p.due_date,
            'status': p.status,
            'receipt_number': p.receipt_number
        } for p in payments])
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Generar número de recibo único
            import random
            receipt_number = f"R-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            
            payment = Payment(
                student_id=data['student_id'],
                concept_id=data['concept_id'],
                amount=data['amount'],
                payment_date=data['payment_date'],
                due_date=data['due_date'],
                receipt_number=receipt_number
            )
            
            db.session.add(payment)
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'payment_id': payment.id, 
                'receipt_number': receipt_number
            })
            
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

# API PARA COMPROBANTE
@app.route('/api/payments/<int:payment_id>/receipt')
def payment_receipt(payment_id):
    try:
        payment = Payment.query.options(
            db.joinedload(Payment.student),
            db.joinedload(Payment.concept)
        ).get(payment_id)
        
        if not payment:
            return jsonify({'success': False, 'error': 'Pago no encontrado'}), 404
        
        receipt_data = {
            'receipt_number': payment.receipt_number,
            'student_name': f"{payment.student.first_name} {payment.student.last_name}",
            'student_dni': payment.student.dni,
            'concept_name': payment.concept.name,
            'amount': payment.amount,
            'payment_date': payment.payment_date,
            'due_date': payment.due_date,
            'status': payment.status,
            'current_date': datetime.now().strftime('%d/%m/%Y')
        }
        
        return jsonify({'success': True, 'receipt': receipt_data})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# AGREGAR DESPUÉS DE LAS APIS DE PAGOS

# CREAR PLAN DE PAGOS
@app.route('/api/payment-plans', methods=['POST'])
def create_payment_plan():
    try:
        data = request.get_json()
        
        # Validar datos
        required_fields = ['student_id', 'concept_id', 'installments', 'start_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Campo faltante: {field}'}), 400
        
        # Obtener concepto
        concept = PaymentConcept.query.get(data['concept_id'])
        if not concept:
            return jsonify({'success': False, 'error': 'Concepto no encontrado'}), 404
        
        total_amount = concept.amount * data['installments']
        
        # Crear plan
        plan = PaymentPlan(
            student_id=data['student_id'],
            concept_id=data['concept_id'],
            total_amount=total_amount,
            installments=data['installments'],
            start_date=data['start_date']
        )
        
        db.session.add(plan)
        db.session.flush()
        
        # Generar cuotas
        create_installments(plan, concept.amount)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'plan_id': plan.id,
            'message': f'Plan creado con {data["installments"]} cuotas'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

def create_installments(plan, monthly_amount):
    from datetime import datetime, timedelta
    
    start_date = datetime.strptime(plan.start_date, '%Y-%m-%d')
    
    for i in range(plan.installments):
        # Fecha emisión: día 1 del mes
        if i == 0:
            emission_date = start_date
        else:
            # Sumar meses correctamente
            next_month = start_date.month + i
            year = start_date.year + (next_month - 1) // 12
            month = (next_month - 1) % 12 + 1
            emission_date = start_date.replace(year=year, month=month, day=1)
        
        # Fecha vencimiento: último día del mes
        if emission_date.month == 12:
            next_month = emission_date.replace(year=emission_date.year + 1, month=1, day=1)
        else:
            next_month = emission_date.replace(month=emission_date.month + 1, day=1)
        
        due_date = next_month - timedelta(days=1)
        
        installment = PaymentInstallment(
            plan_id=plan.id,
            installment_number=i + 1,
            due_date=due_date.strftime('%Y-%m-%d'),
            amount=monthly_amount,
            status='pending'
        )
        
        db.session.add(installment)

# OBTENER PLANES DE PAGO
@app.route('/api/payment-plans')
def get_payment_plans():
    try:
        plans = PaymentPlan.query.options(
            db.joinedload(PaymentPlan.student),
            db.joinedload(PaymentPlan.concept)
        ).all()
        
        result = []
        for plan in plans:
            paid_installments = PaymentInstallment.query.filter_by(
                plan_id=plan.id, 
                status='paid'
            ).count()
            
            result.append({
                'id': plan.id,
                'student_name': f"{plan.student.first_name} {plan.student.last_name}",
                'student_dni': plan.student.dni,
                'concept_name': plan.concept.name,
                'total_amount': plan.total_amount,
                'installments': plan.installments,
                'paid_installments': paid_installments,
                'start_date': plan.start_date,
                'status': plan.status,
                'created_date': plan.created_date
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# OBTENER CUOTAS DE UN PLAN
@app.route('/api/payment-plans/<int:plan_id>/installments')
def get_plan_installments(plan_id):
    try:
        installments = PaymentInstallment.query.filter_by(plan_id=plan_id).order_by(
            PaymentInstallment.installment_number
        ).all()
        
        result = []
        for installment in installments:
            result.append({
                'id': installment.id,
                'installment_number': installment.installment_number,
                'due_date': installment.due_date,
                'amount': installment.amount,
                'status': installment.status,
                'payment_date': installment.payment_date,
                'payment_id': installment.payment_id
            })
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# PAGAR CUOTA
@app.route('/api/installments/<int:installment_id>/pay', methods=['POST'])
def pay_installment(installment_id):
    try:
        data = request.get_json()
        installment = PaymentInstallment.query.get(installment_id)
        
        if not installment:
            return jsonify({'success': False, 'error': 'Cuota no encontrada'}), 404
        
        if installment.status == 'paid':
            return jsonify({'success': False, 'error': 'Esta cuota ya está pagada'}), 400
        
        # Generar número de recibo
        import random
        receipt_number = f"R-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
        
        # Crear pago en el sistema existente
        payment = Payment(
            student_id=installment.plan.student_id,
            concept_id=installment.plan.concept_id,
            amount=installment.amount,
            payment_date=data['payment_date'],
            due_date=installment.due_date,
            receipt_number=receipt_number
        )
        
        db.session.add(payment)
        db.session.flush()
        
        # Actualizar cuota
        installment.status = 'paid'
        installment.payment_date = data['payment_date']
        installment.payment_id = payment.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'payment_id': payment.id,
            'receipt_number': receipt_number,
            'message': 'Cuota pagada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# OBTENER DETALLES DE CUOTA
@app.route('/api/installments/<int:installment_id>')
def get_installment_details(installment_id):
    try:
        installment = PaymentInstallment.query.options(
            db.joinedload(PaymentInstallment.plan).joinedload(PaymentPlan.student),
            db.joinedload(PaymentInstallment.plan).joinedload(PaymentPlan.concept),
            db.joinedload(PaymentInstallment.payment)
        ).get(installment_id)
        
        if not installment:
            return jsonify({'success': False, 'error': 'Cuota no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'installment': {
                'id': installment.id,
                'installment_number': installment.installment_number,
                'due_date': installment.due_date,
                'amount': installment.amount,
                'status': installment.status,
                'payment_date': installment.payment_date,
                'student_name': f"{installment.plan.student.first_name} {installment.plan.student.last_name}",
                'student_dni': installment.plan.student.dni,
                'concept_name': installment.plan.concept.name,
                'payment_id': installment.payment_id
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# APIS PARA ALMACÉN - AGREGAR ANTES DE calculate_age
@app.route('/api/almacen/utiles', methods=['GET', 'POST'])
def utiles_escolares():
    try:
        if request.method == 'GET':
            aula_id = request.args.get('aula_id')
            if aula_id:
                utiles = AlmacenUtil.query.filter_by(aula_id=aula_id).all()
            else:
                utiles = AlmacenUtil.query.all()
            
            result = []
            for util in utiles:
                result.append({
                    'id': util.id,
                    'aula_id': util.aula_id,
                    'material': util.material,
                    'cantidad_requerida': util.cantidad_requerida,
                    'especificaciones': util.especificaciones,
                    'created_at': util.created_at,
                    'aula_nombre': util.aula.name if util.aula else ''
                })
            
            return jsonify(result)
        
        elif request.method == 'POST':
            data = request.get_json()
            
            # Validar campos requeridos
            required_fields = ['aula_id', 'material', 'cantidad_requerida']
            for field in required_fields:
                if not data.get(field):
                    return jsonify({'success': False, 'error': f'Campo requerido faltante: {field}'}), 400
            
            util = AlmacenUtil(
                aula_id=data['aula_id'],
                material=data['material'],
                cantidad_requerida=data['cantidad_requerida'],
                especificaciones=data.get('especificaciones', '')
            )
            
            db.session.add(util)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Material agregado a la lista'})
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/almacen/utiles/<int:util_id>', methods=['DELETE'])
def eliminar_util(util_id):
    try:
        util = AlmacenUtil.query.get(util_id)
        if not util:
            return jsonify({'success': False, 'error': 'Material no encontrado'}), 404
        
        db.session.delete(util)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Material eliminado correctamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/almacen/entregas', methods=['POST'])
def registrar_entrega():
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['estudiante_id', 'util_id', 'cantidad_entregada']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Campo requerido faltante: {field}'}), 400
        
        entrega = AlmacenEntrega(
            estudiante_id=data['estudiante_id'],
            util_id=data['util_id'],
            cantidad_entregada=data['cantidad_entregada'],
            fecha_entrega=data.get('fecha_entrega', datetime.now().strftime('%Y-%m-%d')),
            observaciones=data.get('observaciones', '')
        )
        
        db.session.add(entrega)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Entrega registrada correctamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/almacen/entregas/<int:aula_id>')
def obtener_entregas_aula(aula_id):
    try:
        # Obtener estudiantes del aula
        estudiantes = Student.query.join(Enrollment).filter(
            Enrollment.classroom_id == aula_id,
            Enrollment.status == 'active'
        ).all()
        
        # Obtener útiles del aula
        utiles = AlmacenUtil.query.filter_by(aula_id=aula_id).all()
        
        # Obtener entregas existentes
        entregas = AlmacenEntrega.query.join(AlmacenUtil).filter(
            AlmacenUtil.aula_id == aula_id
        ).all()
        
        result = {
            'estudiantes': [{
                'id': e.id,
                'nombre': f"{e.first_name} {e.last_name}",
                'dni': e.dni
            } for e in estudiantes],
            'utiles': [{
                'id': u.id,
                'material': u.material,
                'cantidad_requerida': u.cantidad_requerida,
                'especificaciones': u.especificaciones
            } for u in utiles],
            'entregas': [{
                'id': e.id,
                'estudiante_id': e.estudiante_id,
                'util_id': e.util_id,
                'cantidad_entregada': e.cantidad_entregada,
                'fecha_entrega': e.fecha_entrega,
                'observaciones': e.observaciones
            } for e in entregas]
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# REPORTES - AGREGAR DESPUÉS DE LAS ÚLTIMAS APIS EXISTENTES

@app.route('/api/reportes/estudiantes-por-aula')
def reporte_estudiantes_por_aula():
    """Reporte 1: Lista de estudiantes por aula"""
    try:
        aula_id = request.args.get('aula_id')
        
        query = Student.query.join(Enrollment).join(Classroom).filter(
            Enrollment.status == 'active'
        )
        
        if aula_id:
            query = query.filter(Enrollment.classroom_id == aula_id)
        
        estudiantes = query.all()
        
        result = []
        for estudiante in estudiantes:
            # Encontrar la matrícula activa
            matricula = next((e for e in estudiante.enrollments if e.status == 'active'), None)
            if matricula:
                result.append({
                    'id': estudiante.id,
                    'nombre_completo': f"{estudiante.first_name} {estudiante.last_name}",
                    'dni': estudiante.dni,
                    'edad': calculate_age(estudiante.birth_date),
                    'telefono': estudiante.phone,
                    'aula': matricula.classroom.name,
                    'aula_id': matricula.classroom_id
                })
        
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        print("Error en reporte estudiantes:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reportes/cuotas-vencidas')
def reporte_cuotas_vencidas():
    """Reporte 2: Cuotas vencidas por alumno"""
    try:
        from datetime import datetime
        
        hoy = datetime.now().date()
        
        # Obtener cuotas vencidas
        cuotas_vencidas = PaymentInstallment.query.join(
            PaymentPlan
        ).join(
            Student
        ).join(
            Enrollment
        ).join(
            Classroom
        ).filter(
            PaymentInstallment.status == 'pending',
            PaymentInstallment.due_date < hoy.strftime('%Y-%m-%d')
        ).all()
        
        result = []
        total_adeudado = 0
        
        for cuota in cuotas_vencidas:
            dias_mora = (hoy - datetime.strptime(cuota.due_date, '%Y-%m-%d').date()).days
            
            result.append({
                'alumno_id': cuota.plan.student.id,
                'alumno_nombre': f"{cuota.plan.student.first_name} {cuota.plan.student.last_name}",
                'alumno_dni': cuota.plan.student.dni,
                'aula': cuota.plan.student.enrollments[0].classroom.name if cuota.plan.student.enrollments else 'Sin aula',
                'concepto': cuota.plan.concept.name,
                'cuota_numero': cuota.installment_number,
                'monto': cuota.amount,
                'fecha_vencimiento': cuota.due_date,
                'dias_mora': dias_mora
            })
            total_adeudado += cuota.amount
        
        return jsonify({
            'success': True, 
            'data': result,
            'total_adeudado': total_adeudado,
            'total_cuotas': len(result)
        })
        
    except Exception as e:
        print("Error en reporte cuotas vencidas:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reportes/stock-bajo')
def reporte_stock_bajo():
    """Reporte 3: Materiales con stock bajo"""
    try:
        materiales = MaterialAula.query.filter(
            MaterialAula.stock_actual <= MaterialAula.stock_minimo
        ).all()
        
        result = []
        for material in materiales:
            estado = 'CRÍTICO' if material.stock_actual == 0 else 'BAJO'
            result.append({
                'id': material.id,
                'nombre': material.nombre,
                'categoria': material.categoria,
                'stock_actual': material.stock_actual,
                'stock_minimo': material.stock_minimo,
                'unidad_medida': material.unidad_medida,
                'diferencia': material.stock_minimo - material.stock_actual,
                'estado': estado,
                'ubicacion': material.ubicacion or 'No especificada'
            })
        
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        print("Error en reporte stock bajo:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reportes/resumen-matriculas')
def reporte_resumen_matriculas():
    """Reporte 4: Resumen de matrículas por aula"""
    try:
        aulas = Classroom.query.all()
        
        result = []
        total_matriculados = 0
        total_capacidad = 0
        
        for aula in aulas:
            matriculados = Enrollment.query.filter_by(
                classroom_id=aula.id, 
                status='active'
            ).count()
            
            result.append({
                'aula_id': aula.id,
                'aula_nombre': aula.name,
                'edad_rango': aula.age_range,
                'capacidad': aula.capacity,
                'matriculados': matriculados,
                'cupos_disponibles': aula.capacity - matriculados,
                'porcentaje_ocupacion': round((matriculados / aula.capacity) * 100, 1) if aula.capacity > 0 else 0
            })
            
            total_matriculados += matriculados
            total_capacidad += aula.capacity
        
        return jsonify({
            'success': True, 
            'data': result,
            'totales': {
                'total_aulas': len(aulas),
                'total_matriculados': total_matriculados,
                'total_capacidad': total_capacidad,
                'porcentaje_total': round((total_matriculados / total_capacidad) * 100, 1) if total_capacidad > 0 else 0
            }
        })
        
    except Exception as e:
        print("Error en reporte resumen matrículas:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reportes/utiles-pendientes')
def reporte_utiles_pendientes():
    """Reporte 5: Útiles pendientes por aula"""
    try:
        aula_id = request.args.get('aula_id')
        
        # Obtener aulas
        query = Classroom.query
        if aula_id:
            query = query.filter(Classroom.id == aula_id)
        aulas = query.all()
        
        result = []
        
        for aula in aulas:
            # Obtener útiles configurados para el aula
            utiles = AlmacenUtil.query.filter_by(aula_id=aula.id).all()
            
            aula_data = {
                'aula_id': aula.id,
                'aula_nombre': aula.name,
                'utiles': []
            }
            
            for util in utiles:
                # Obtener estudiantes del aula
                estudiantes = Student.query.join(Enrollment).filter(
                    Enrollment.classroom_id == aula.id,
                    Enrollment.status == 'active'
                ).all()
                
                total_pendiente = 0
                estudiantes_con_faltantes = 0
                
                for estudiante in estudiantes:
                    # Obtener entregas de este útil
                    entregas = AlmacenEntrega.query.filter_by(
                        estudiante_id=estudiante.id,
                        util_id=util.id
                    ).all()
                    
                    total_entregado = sum(e.cantidad_entregada for e in entregas)
                    pendiente = util.cantidad_requerida - total_entregado
                    
                    if pendiente > 0:
                        total_pendiente += pendiente
                        estudiantes_con_faltantes += 1
                
                if total_pendiente > 0:
                    aula_data['utiles'].append({
                        'material': util.material,
                        'cantidad_requerida': util.cantidad_requerida,
                        'total_pendiente': total_pendiente,
                        'estudiantes_con_faltantes': estudiantes_con_faltantes,
                        'especificaciones': util.especificaciones or 'No especificado'
                    })
            
            if aula_data['utiles']:  # Solo agregar aulas con útiles pendientes
                result.append(aula_data)
        
        return jsonify({'success': True, 'data': result})
        
    except Exception as e:
        print("Error en reporte útiles pendientes:", str(e))
        return jsonify({'success': False, 'error': str(e)}), 500

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
