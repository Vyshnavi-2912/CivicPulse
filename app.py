import os
import uuid
import datetime
import sqlite3
from flask import (
    Flask, render_template, request, redirect, url_for, flash, jsonify, session
)
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'civicpulse.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

app = Flask(__name__)
app.secret_key = 'civicpulse_hackathon_sdg11_secret_key_2026'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB limit

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ==============================================================================
# GEOLOCATION FALLBACK ENGINE
# ==============================================================================
import random

KNOWN_COORDINATES = {
    'eluru': (16.7107, 81.0952),
    'kovvur': (17.0145, 81.7302),
    'rajahmundry': (16.9891, 81.7835),
    'vijayawada': (16.5062, 80.6480),
    'visakhapatnam': (17.6868, 83.2185),
    'guntur': (16.3067, 80.4365),
    'tirupati': (13.6288, 79.4192),
    'kakinada': (16.9891, 82.2475),
    'west godavari': (16.9000, 81.5000),
    'east godavari': (17.0000, 82.0000),
    'krishna': (16.5000, 80.8000),
    'andhra pradesh': (16.5000, 80.6480),
    
    'hyderabad': (17.3850, 78.4867),
    'warangal': (17.9784, 79.5941),
    'telangana': (17.3850, 78.4867),
    
    'meerut': (28.9845, 77.7064),
    'rampur': (28.8073, 79.0261),
    'lucknow': (26.8467, 80.9462),
    'kanpur': (26.4499, 80.3319),
    'noida': (28.5355, 77.3910),
    'uttar pradesh': (26.8467, 80.9462),
    
    'hoshangabad': (22.7441, 77.7369),
    'pipariya': (22.7601, 78.3550),
    'bhopal': (23.2599, 77.4126),
    'indore': (22.7196, 75.8577),
    'madhya pradesh': (23.2599, 77.4126),
    
    'mandya': (12.5218, 76.8951),
    'bengaluru': (12.9716, 77.5946),
    'bangalore': (12.9716, 77.5946),
    'mysuru': (12.2958, 76.6394),
    'karnataka': (12.9716, 77.5946),
    
    'siliguri': (26.7161, 88.4236),
    'darjeeling': (27.0410, 88.2663),
    'kolkata': (22.5726, 88.3639),
    'west bengal': (22.5726, 88.3639),
    
    'chennai': (13.0827, 80.2707),
    'coimbatore': (11.0168, 76.9558),
    'tamil nadu': (13.0827, 80.2707),
    
    'mumbai': (19.0760, 72.8777),
    'pune': (18.5204, 73.8567),
    'maharashtra': (19.0760, 72.8777),
    
    'delhi': (28.6139, 77.2090),
    'new delhi': (28.6139, 77.2090),
    
    'kochi': (9.9312, 76.2673),
    'thiruvananthapuram': (8.5241, 76.9366),
    'kerala': (8.5241, 76.9366)
}

def estimate_coordinates(state, district, village_city):
    """Estimate latitude/longitude if citizen didn't provide GPS coordinates"""
    search_keys = [
        village_city.lower().strip() if village_city else '',
        district.lower().strip() if district else '',
        state.lower().strip() if state else ''
    ]

    for key in search_keys:
        if not key:
            continue
        for name, coords in KNOWN_COORDINATES.items():
            if name in key or key in name:
                lat = coords[0] + random.uniform(-0.006, 0.006)
                lng = coords[1] + random.uniform(-0.006, 0.006)
                return round(lat, 6), round(lng, 6)

    # India center fallback with jitter
    return round(20.5937 + random.uniform(-1.5, 1.5), 6), round(78.9629 + random.uniform(-1.5, 1.5), 6)

# ==============================================================================
# RULE-BASED SEVERITY ASSESSMENT ENGINE
# ==============================================================================
def calculate_severity(category, safety_risk='none', extent_damage='moderate', location_type='standard'):
    """
    Transparent rule-based priority engine.
    Categories: Pothole, Damaged Road, Broken Streetlight, Garbage Accumulation, Water Leakage, Fallen Tree, Unsafe Electrical Pole or Wire, Other
    """
    score = 0
    reasons = []

    # Category base weight
    cat_weights = {
        'Unsafe Electrical Pole or Wire': 4,
        'Water Leakage': 3,
        'Pothole': 3,
        'Damaged Road': 2,
        'Fallen Tree': 3,
        'Broken Streetlight': 2,
        'Garbage Accumulation': 2,
        'Other': 1
    }
    score += cat_weights.get(category, 1)

    # Safety Risk modifier
    if safety_risk == 'high_hazard': # Live wires, active obstruction on highway, water near school/hospital
        score += 4
        reasons.append("Presents immediate physical safety hazard to commuters or residents")
    elif safety_risk == 'moderate_hazard':
        score += 2
        reasons.append("Moderate risk of vehicle damage or minor injury")

    # Extent of damage
    if extent_damage == 'severe':
        score += 3
        reasons.append("Severe physical damage or infrastructure breakdown")
    elif extent_damage == 'moderate':
        score += 1
        reasons.append("Moderate structural wear or accumulation")

    # Location priority multiplier
    if location_type == 'main_road':
        score += 3
        reasons.append("Located on a high-density main access route or highway junction")
    elif location_type == 'public_facility': # School, hospital, market
        score += 2
        reasons.append("Proximity to a busy public facility (school, market, hospital)")
    else:
        reasons.append("Standard residential or rural lane location")

    # Final Level Assignment
    if score >= 9:
        level = 'Critical'
    elif score >= 6:
        level = 'High'
    elif score >= 4:
        level = 'Medium'
    else:
        level = 'Low'

    reason_str = f"Assigned {level.upper()} severity: " + "; ".join(reasons) + "."
    return level, reason_str


# ==============================================================================
# MODULAR AI CLASSIFIER DEMO MODULE
# ==============================================================================
def predict_category_ai(filepath):
    """
    Modular image classification predictor.
    Uses image analysis heuristic / rule demo mode with explicit disclaimer.
    Designed so a real PyTorch/TensorFlow Model can replace this function.
    """
    filename = os.path.basename(filepath).lower()
    
    # Simple rule heuristic based on filename keywords or fallback predictions for demo
    if 'pothole' in filename:
        cat = 'Pothole'
        conf = 0.91
    elif 'garbage' in filename or 'waste' in filename:
        cat = 'Garbage Accumulation'
        conf = 0.89
    elif 'water' in filename or 'leak' in filename:
        cat = 'Water Leakage'
        conf = 0.93
    elif 'light' in filename or 'pole' in filename or 'street' in filename:
        cat = 'Broken Streetlight'
        conf = 0.86
    elif 'tree' in filename or 'branch' in filename:
        cat = 'Fallen Tree'
        conf = 0.88
    elif 'wire' in filename or 'electric' in filename:
        cat = 'Unsafe Electrical Pole or Wire'
        conf = 0.94
    else:
        # Default smart fallback prediction for uploaded demo images
        cat = 'Pothole'
        conf = 0.82

    return {
        'predicted_category': cat,
        'confidence': conf,
        'confidence_percent': f"{int(conf * 100)}%",
        'is_demo_mode': True,
        'model_name': 'CivicPulse-V1 Vision Classifier (Demonstration Mode)',
        'disclaimer': 'AI predictions are preliminary demonstration estimates and require citizen verification before official logging.'
    }


# ==============================================================================
# MAP DEPARTMENT MAPPING
# ==============================================================================
def get_department_for_category(category):
    dept_map = {
        'Pothole': 'Road Maintenance Department',
        'Damaged Road': 'Road Maintenance Department',
        'Broken Streetlight': 'Electricity Board / DISCOM',
        'Unsafe Electrical Pole or Wire': 'Electricity Board / DISCOM',
        'Garbage Accumulation': 'Sanitation Department',
        'Water Leakage': 'Water Supply & Sanitation Department',
        'Fallen Tree': 'Public Works Department (PWD)',
        'Other': 'Gram Panchayat'
    }
    return dept_map.get(category, 'Gram Panchayat')


# ==============================================================================
# ROUTES
# ==============================================================================

@app.route('/')
def index():
    conn = get_db_connection()
    
    # Calculate real DB stats
    total_count = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    open_count = conn.execute("SELECT COUNT(*) FROM reports WHERE status IN ('Reported', 'Under Review', 'In Progress')").fetchone()[0]
    high_critical_count = conn.execute("SELECT COUNT(*) FROM reports WHERE severity_level IN ('High', 'Critical')").fetchone()[0]
    resolved_count = conn.execute("SELECT COUNT(*) FROM reports WHERE status = 'Resolved'").fetchone()[0]
    
    # Recent reports
    recent_reports = conn.execute(
        "SELECT * FROM reports ORDER BY submission_date DESC LIMIT 4"
    ).fetchall()
    
    conn.close()
    
    return render_template(
        'index.html',
        total_count=total_count,
        open_count=open_count,
        high_critical_count=high_critical_count,
        resolved_count=resolved_count,
        recent_reports=recent_reports
    )


@app.route('/report', methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        # Form inputs
        category = request.form.get('category')
        state = request.form.get('state')
        district = request.form.get('district')
        village_city = request.form.get('village_city')
        mandal_municipality = request.form.get('mandal_municipality', '')
        landmark = request.form.get('landmark', '')
        description = request.form.get('description')
        observation_date = request.form.get('observation_date')
        
        # Risk factors for severity
        safety_risk = request.form.get('safety_risk', 'none')
        extent_damage = request.form.get('extent_damage', 'moderate')
        location_type = request.form.get('location_type', 'standard')
        
        # Geolocation check with fallback
        lat = request.form.get('latitude', '')
        lng = request.form.get('longitude', '')
        try:
            latitude = float(lat) if lat else None
            longitude = float(lng) if lng else None
        except (ValueError, TypeError):
            latitude, longitude = None, None

        if latitude is None or longitude is None:
            latitude, longitude = estimate_coordinates(state, district, village_city)

        # Validation
        if not category or not state or not district or not village_city or not description or not observation_date:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('report'))

        if 'image' not in request.files:
            flash('Please upload an image of the problem.', 'danger')
            return redirect(url_for('report'))

        file = request.files['image']
        if file.filename == '':
            flash('No image selected for upload.', 'danger')
            return redirect(url_for('report'))

        if not allowed_file(file.filename):
            flash('Invalid image format! Allowed formats: PNG, JPG, JPEG, WEBP, GIF.', 'danger')
            return redirect(url_for('report'))

        # Secure file saving
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"user_{uuid.uuid4().hex[:10]}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)

        # AI Prediction check
        ai_res = predict_category_ai(filepath)
        ai_detected = ai_res['predicted_category']
        ai_conf = ai_res['confidence']

        # Rule-based Severity Engine
        severity_level, severity_reason = calculate_severity(
            category=category,
            safety_risk=safety_risk,
            extent_damage=extent_damage,
            location_type=location_type
        )

        # Unique Report ID
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        rand_suffix = uuid.uuid4().hex[:4].upper()
        report_id = f"CP-{date_str}-{rand_suffix}"

        # DB Insertion
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO reports (
                id, category, description, image_path, state, district, village_city,
                mandal_municipality, landmark, latitude, longitude, observation_date,
                severity_level, severity_reason, status, ai_detected_category,
                ai_confidence, is_sample, upvotes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
        ''', (
            report_id, category, description, unique_filename, state, district, village_city,
            mandal_municipality, landmark, latitude, longitude, observation_date,
            severity_level, severity_reason, 'Reported', ai_detected, ai_conf
        ))
        conn.commit()
        conn.close()

        flash(f'Report submitted successfully! Report ID: {report_id}', 'success')
        return redirect(url_for('report_details', report_id=report_id))

    today_date = datetime.date.today().isoformat()
    return render_template('report.html', today_date=today_date)


@app.route('/api/ai-analyze', methods=['POST'])
def api_ai_analyze():
    """Asynchronous endpoint for frontend AI analysis preview"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
    file = request.files['image']
    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid image file'}), 400

    ext = file.filename.rsplit('.', 1)[1].lower()
    temp_filename = f"temp_ai_{uuid.uuid4().hex[:8]}.{ext}"
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
    file.save(temp_path)

    res = predict_category_ai(temp_path)
    
    # Remove temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)

    return jsonify(res)


@app.route('/api/assess-severity', methods=['POST'])
def api_assess_severity():
    """Asynchronous endpoint for frontend dynamic severity calculation preview"""
    data = request.get_json() or {}
    category = data.get('category', 'Other')
    safety_risk = data.get('safety_risk', 'none')
    extent_damage = data.get('extent_damage', 'moderate')
    location_type = data.get('location_type', 'standard')

    level, reason = calculate_severity(category, safety_risk, extent_damage, location_type)
    return jsonify({
        'severity_level': level,
        'severity_reason': reason
    })


@app.route('/reports')
def reports():
    category = request.args.get('category', '')
    district = request.args.get('district', '')
    severity = request.args.get('severity', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    source = request.args.get('source', '') # 'real', 'sample', or ''

    query = "SELECT * FROM reports WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if district:
        query += " AND (district LIKE ? OR village_city LIKE ?)"
        params.append(f"%{district}%")
        params.append(f"%{district}%")
    if severity:
        query += " AND severity_level = ?"
        params.append(severity)
    if status:
        query += " AND status = ?"
        params.append(status)
    if source == 'real':
        query += " AND is_sample = 0"
    elif source == 'sample':
        query += " AND is_sample = 1"
    if search:
        query += " AND (id LIKE ? OR description LIKE ? OR village_city LIKE ? OR district LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY submission_date DESC"

    conn = get_db_connection()
    reports_list = conn.execute(query, params).fetchall()
    
    # Get distinct categories & districts for filter dropdowns
    categories = [r[0] for r in conn.execute("SELECT DISTINCT category FROM reports").fetchall()]
    districts = [r[0] for r in conn.execute("SELECT DISTINCT district FROM reports").fetchall()]
    conn.close()

    return render_template(
        'reports.html',
        reports=reports_list,
        categories=categories,
        districts=districts,
        selected_category=category,
        selected_district=district,
        selected_severity=severity,
        selected_status=status,
        selected_source=source,
        search_query=search
    )


@app.route('/api/reports')
def api_reports():
    """API endpoint for Leaflet Map markers and dynamic AJAX filters"""
    category = request.args.get('category', '')
    district = request.args.get('district', '')
    severity = request.args.get('severity', '')
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    source = request.args.get('source', '')

    query = "SELECT * FROM reports WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if district:
        query += " AND (district LIKE ? OR village_city LIKE ? OR state LIKE ?)"
        params.extend([f"%{district}%", f"%{district}%", f"%{district}%"])
    if severity:
        query += " AND severity_level = ?"
        params.append(severity)
    if status:
        query += " AND status = ?"
        params.append(status)
    if source == 'real':
        query += " AND is_sample = 0"
    elif source == 'sample':
        query += " AND is_sample = 1"
    if search:
        query += " AND (id LIKE ? OR description LIKE ? OR village_city LIKE ? OR district LIKE ? OR category LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY submission_date DESC"

    conn = get_db_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()

    result = []
    for r in rows:
        result.append({
            'id': r['id'],
            'category': r['category'],
            'description': r['description'],
            'image_path': url_for('static', filename=f'uploads/{r["image_path"]}'),
            'state': r['state'],
            'district': r['district'],
            'village_city': r['village_city'],
            'mandal_municipality': r['mandal_municipality'],
            'landmark': r['landmark'],
            'latitude': r['latitude'],
            'longitude': r['longitude'],
            'observation_date': r['observation_date'],
            'submission_date': r['submission_date'],
            'severity_level': r['severity_level'],
            'severity_reason': r['severity_reason'],
            'status': r['status'],
            'is_sample': bool(r['is_sample']),
            'upvotes': r['upvotes']
        })
    return jsonify(result)


@app.route('/report/<report_id>')
def report_details(report_id):
    conn = get_db_connection()
    report_item = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()

    if not report_item:
        conn.close()
        flash('Report not found!', 'danger')
        return redirect(url_for('reports'))

    target_dept = get_department_for_category(report_item['category'])

    # Find matching authority contact using robust cascading location match
    clean_dist = report_item['district'].replace('District', '').strip() if report_item['district'] else ''
    clean_state = report_item['state'].strip() if report_item['state'] else ''

    # 1. Exact or substring match on department and district
    authority = conn.execute('''
        SELECT * FROM authority_contacts 
        WHERE department = ? AND (district LIKE ? OR ? LIKE '%' || district || '%')
        ORDER BY is_verified DESC LIMIT 1
    ''', (target_dept, f"%{clean_dist}%", clean_dist)).fetchone()

    # 2. Match department and state
    if not authority:
        authority = conn.execute('''
            SELECT * FROM authority_contacts 
            WHERE department = ? AND (state LIKE ? OR ? LIKE '%' || state || '%')
            ORDER BY is_verified DESC LIMIT 1
        ''', (target_dept, f"%{clean_state}%", clean_state)).fetchone()

    # 3. Match any department in that district
    if not authority:
        authority = conn.execute('''
            SELECT * FROM authority_contacts 
            WHERE (district LIKE ? OR ? LIKE '%' || district || '%')
            ORDER BY is_verified DESC LIMIT 1
        ''', (f"%{clean_dist}%", clean_dist)).fetchone()

    # 4. Fallback: match any authority in the state or default first verified
    if not authority:
        authority = conn.execute('''
            SELECT * FROM authority_contacts 
            WHERE (state LIKE ? OR ? LIKE '%' || state || '%')
            ORDER BY is_verified DESC LIMIT 1
        ''', (f"%{clean_state}%", clean_state)).fetchone()

    if not authority:
        authority = conn.execute('SELECT * FROM authority_contacts ORDER BY id ASC LIMIT 1').fetchone()

    conn.close()

    return render_template(
        'report_details.html',
        report=report_item,
        authority=authority,
        target_department=target_dept
    )


@app.route('/api/report/<report_id>/upvote', methods=['POST'])
def api_upvote(report_id):
    conn = get_db_connection()
    conn.execute("UPDATE reports SET upvotes = upvotes + 1 WHERE id = ?", (report_id,))
    conn.commit()
    new_upvotes = conn.execute("SELECT upvotes FROM reports WHERE id = ?", (report_id,)).fetchone()[0]
    conn.close()
    return jsonify({'success': True, 'new_upvotes': new_upvotes})


@app.route('/dashboard')
def dashboard():
    conn = get_db_connection()

    # Aggregations
    total = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
    open_count = conn.execute("SELECT COUNT(*) FROM reports WHERE status IN ('Reported', 'Under Review', 'In Progress')").fetchone()[0]
    high_critical = conn.execute("SELECT COUNT(*) FROM reports WHERE severity_level IN ('High', 'Critical')").fetchone()[0]
    resolved = conn.execute("SELECT COUNT(*) FROM reports WHERE status = 'Resolved'").fetchone()[0]
    real_count = conn.execute("SELECT COUNT(*) FROM reports WHERE is_sample = 0").fetchone()[0]
    sample_count = conn.execute("SELECT COUNT(*) FROM reports WHERE is_sample = 1").fetchone()[0]

    # Category breakdown
    cat_rows = conn.execute("SELECT category, COUNT(*) as cnt FROM reports GROUP BY category").fetchall()
    categories_data = {r['category']: r['cnt'] for r in cat_rows}

    # Status breakdown
    status_rows = conn.execute("SELECT status, COUNT(*) as cnt FROM reports GROUP BY status").fetchall()
    status_data = {r['status']: r['cnt'] for r in status_rows}

    # Severity breakdown
    sev_rows = conn.execute("SELECT severity_level, COUNT(*) as cnt FROM reports GROUP BY severity_level").fetchall()
    severity_data = {r['severity_level']: r['cnt'] for r in sev_rows}

    # Location breakdown (by district)
    dist_rows = conn.execute("SELECT district, COUNT(*) as cnt FROM reports GROUP BY district ORDER BY cnt DESC LIMIT 6").fetchall()
    district_data = {r['district']: r['cnt'] for r in dist_rows}

    # Recent submissions
    recent_reports = conn.execute("SELECT * FROM reports ORDER BY submission_date DESC LIMIT 5").fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        total=total,
        open_count=open_count,
        high_critical=high_critical,
        resolved=resolved,
        real_count=real_count,
        sample_count=sample_count,
        categories_data=categories_data,
        status_data=status_data,
        severity_data=severity_data,
        district_data=district_data,
        recent_reports=recent_reports
    )


@app.route('/authority')
def authority():
    state = request.args.get('state', '')
    district = request.args.get('district', '')
    department = request.args.get('department', '')
    search = request.args.get('search', '')

    query = "SELECT * FROM authority_contacts WHERE 1=1"
    params = []

    if state:
        query += " AND state LIKE ?"
        params.append(f"%{state}%")
    if district:
        query += " AND district LIKE ?"
        params.append(f"%{district}%")
    if department:
        query += " AND department = ?"
        params.append(department)
    if search:
        query += " AND (office_name LIKE ? OR district LIKE ? OR mandal_municipality LIKE ? OR address LIKE ? OR contact_person LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%", f"%{search}%"])

    query += " ORDER BY is_verified DESC, state ASC, district ASC"

    conn = get_db_connection()
    contacts = conn.execute(query, params).fetchall()
    states = [r[0] for r in conn.execute("SELECT DISTINCT state FROM authority_contacts ORDER BY state ASC").fetchall()]
    departments = [r[0] for r in conn.execute("SELECT DISTINCT department FROM authority_contacts ORDER BY department ASC").fetchall()]
    conn.close()

    return render_template(
        'authority.html',
        contacts=contacts,
        states=states,
        departments=departments,
        selected_state=state,
        selected_district=district,
        selected_department=department,
        search_query=search
    )


@app.route('/about')
def about():
    return render_template('about.html')


# ==============================================================================
# ADMINISTRATIVE DEMO PANEL
# ==============================================================================
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'login':
            username = request.form.get('username')
            password = request.form.get('password')
            if username == 'admin' and password == 'civicpulse2026':
                session['is_admin'] = True
                flash('Successfully logged in as Admin Demonstration Officer.', 'success')
            else:
                flash('Invalid administrator credentials!', 'danger')
            return redirect(url_for('admin'))

    if not session.get('is_admin'):
        return render_template('admin_login.html')

    conn = get_db_connection()
    reports_list = conn.execute("SELECT * FROM reports ORDER BY submission_date DESC").fetchall()
    authorities_list = conn.execute("SELECT * FROM authority_contacts ORDER BY id DESC").fetchall()
    conn.close()

    return render_template('admin.html', reports=reports_list, authorities=authorities_list)


@app.route('/admin/update-status', methods=['POST'])
def admin_update_status():
    if not session.get('is_admin'):
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('admin'))

    report_id = request.form.get('report_id')
    new_status = request.form.get('status')

    if report_id and new_status:
        conn = get_db_connection()
        conn.execute("UPDATE reports SET status = ? WHERE id = ?", (new_status, report_id))
        conn.commit()
        conn.close()
        flash(f'Report {report_id} status updated to {new_status}.', 'success')

    return redirect(url_for('admin'))


@app.route('/admin/add-authority', methods=['POST'])
def admin_add_authority():
    if not session.get('is_admin'):
        flash('Unauthorized action!', 'danger')
        return redirect(url_for('admin'))

    state = request.form.get('state')
    district = request.form.get('district')
    mandal = request.form.get('mandal_municipality', '')
    department = request.form.get('department')
    office_name = request.form.get('office_name')
    contact_person = request.form.get('contact_person', '')
    phone = request.form.get('phone', '')
    email = request.form.get('email', '')
    address = request.form.get('address', '')

    if state and district and department and office_name:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO authority_contacts (
                state, district, mandal_municipality, department, office_name,
                contact_person, phone, email, address, is_verified, verification_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 'Verified via Admin Panel Demo')
        ''', (state, district, mandal, department, office_name, contact_person, phone, email, address))
        conn.commit()
        conn.close()
        flash('New Verified Local Authority Contact added successfully!', 'success')
    else:
        flash('Missing required fields for authority contact!', 'danger')

    return redirect(url_for('admin'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    flash('Logged out of Admin Demonstration mode.', 'info')
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
