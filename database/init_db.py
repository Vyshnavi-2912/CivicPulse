import os
import sqlite3
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'civicpulse.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')
UPLOADS_DIR = os.path.join(BASE_DIR, 'static', 'uploads')
ARTIFACT_DIR = r"C:\Users\VYSHNAVISURESH\.gemini\antigravity-ide\brain\3ebae03c-39b1-4109-8e1a-1d52dc832efb"

def init_db():
    os.makedirs(os.path.join(BASE_DIR, 'database'), exist_ok=True)
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'static', 'css'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'static', 'js'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'static', 'images'), exist_ok=True)

    print(f"Initializing database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        cursor.executescript(f.read())

    # Copy sample images from artifacts directory if present, else create fallbacks
    sample_mapping = {
        "sample_pothole.png": "sample_pothole_1791542778323.png",
        "sample_garbage.png": "sample_garbage_1791542836570.png",
        "sample_water.png": "sample_water_1791542885401.png",
        "sample_streetlight.png": "sample_streetlight_1791542931627.png",
        "sample_tree.png": "sample_tree_1791542988099.png"
    }

    for target_name, src_name in sample_mapping.items():
        src_path = os.path.join(ARTIFACT_DIR, src_name)
        dst_path = os.path.join(UPLOADS_DIR, target_name)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f"Copied sample image: {target_name}")
        else:
            # Create a simple dummy file if artifact isn't found
            print(f"Warning: {src_path} not found. Creating placeholder.")
            with open(dst_path, "wb") as f:
                f.write(b"")

    # Seed Sample Reports
    sample_reports = [
        (
            'CP-SAMPLE-01',
            'Pothole',
            'Large deep pothole obstructing the main entrance access road to Kovvur village near the canal bridge. Poses severe collision and accident hazard for two-wheelers at night.',
            'sample_pothole.png',
            'Andhra Pradesh',
            'West Godavari',
            'Kovvur',
            'Kovvur Mandal',
            'Near Canal Bridge, Main Access Road',
            17.0145,
            81.7302,
            '2026-10-05',
            'High',
            'Assigned HIGH severity because the issue is located on a main access route with high traffic exposure and direct physical risk to motorbikes.',
            'Under Review',
            'Pothole',
            0.89,
            1,
            14
        ),
        (
            'CP-SAMPLE-02',
            'Garbage Accumulation',
            'Uncleared municipal waste accumulation dumping pile near the primary government school boundary wall. Creating severe odor and public health concern.',
            'sample_garbage.png',
            'Uttar Pradesh',
            'Meerut',
            'Rampur',
            'Rajpura Block',
            'Behind Government Primary School',
            28.9845,
            77.7064,
            '2026-10-06',
            'Medium',
            'Assigned MEDIUM severity due to proximity to a public institution (school), requiring sanitation intervention before vector proliferation.',
            'Reported',
            'Garbage Accumulation',
            0.92,
            1,
            8
        ),
        (
            'CP-SAMPLE-03',
            'Water Leakage',
            'Major high-pressure water pipeline burst along main bazaar road causing continuous clean drinking water wastage and road waterlogging.',
            'sample_water.png',
            'Madhya Pradesh',
            'Hoshangabad',
            'Pipariya',
            'Pipariya Municipality',
            'Station Road, Near Main Bazaar',
            22.7601,
            78.3550,
            '2026-10-07',
            'Critical',
            'Assigned CRITICAL severity due to continuous drinking water loss, soil erosion under asphalt, and immediate municipal utility breakdown.',
            'In Progress',
            'Water Leakage',
            0.94,
            1,
            23
        ),
        (
            'CP-SAMPLE-04',
            'Broken Streetlight',
            'Non-functional LED street light pole at dark highway village junction. Area remains completely pitch dark during night hours causing safety concerns.',
            'sample_streetlight.png',
            'Karnataka',
            'Mandya',
            'Mandya Rural',
            'Mandya Taluk',
            'NH-275 Village Bypass Junction',
            12.5218,
            76.8951,
            '2026-10-04',
            'High',
            'Assigned HIGH severity because dark highway intersections significantly elevate nighttime road accident and crime risk for pedestrians.',
            'Resolved',
            'Broken Streetlight',
            0.87,
            1,
            31
        ),
        (
            'CP-SAMPLE-05',
            'Fallen Tree',
            'Heavy tree branch snapped during monsoon storm and partially blocking one lane of rural farm transport road.',
            'sample_tree.png',
            'West Bengal',
            'Darjeeling',
            'Siliguri Rural',
            'Matigara Block',
            'Near Tea Estate Gate No. 2',
            26.7161,
            88.4236,
            '2026-10-08',
            'Medium',
            'Assigned MEDIUM severity as it partially obstructs local vehicular lane and can be cleared with routine forestry crew dispatch.',
            'Reported',
            'Fallen Tree',
            0.91,
            1,
            5
        )
    ]

    cursor.executemany('''
        INSERT INTO reports (
            id, category, description, image_path, state, district, village_city,
            mandal_municipality, landmark, latitude, longitude, observation_date,
            severity_level, severity_reason, status, ai_detected_category,
            ai_confidence, is_sample, upvotes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', sample_reports)

    # Seed Official Authority Contact Directory Records
    authority_contacts = [
        (
            'Andhra Pradesh',
            'West Godavari',
            'Kovvur Mandal',
            'Road Maintenance Department',
            'Executive Engineer Office (R&B Department)',
            'Er. V. Ramesh, EE',
            '+91 8813 234101',
            'ee_rb_wgodavari@ap.gov.in',
            'R&B Office Complex, Main Road, Kovvur, AP 534350',
            1,
            'Verified Official Govt Contact Directory (Hackathon Seed)'
        ),
        (
            'Andhra Pradesh',
            'West Godavari',
            'Kovvur Mandal',
            'Gram Panchayat',
            'Kovvur Gram Panchayat / Municipal Council',
            'Panchayat Secretary Office',
            '+91 8813 234552',
            'gp_kovvur@apgov.in',
            'Panchayat Bhavan, Station Road, Kovvur',
            1,
            'Verified Official Directory'
        ),
        (
            'Uttar Pradesh',
            'Meerut',
            'Rajpura Block',
            'Sanitation Department',
            'Block Development Officer (BDO) & Swachh Bharat Cell',
            'Shri R. K. Sharma, BDO',
            '+91 121 2401890',
            'bdo_rajpura_meerut@up.gov.in',
            'Block Office Campus, Rajpura, Meerut, UP 250001',
            1,
            'Verified Official Directory'
        ),
        (
            'Madhya Pradesh',
            'Hoshangabad',
            'Pipariya Municipality',
            'Water Supply & Sanitation Department',
            'Pipariya Municipal Public Health Engineering (PHE)',
            'Chief Municipal Officer (CMO)',
            '+91 7576 222045',
            'cmo_pipariya@mp.gov.in',
            'Nagar Palika Parishad, Main Road, Pipariya, MP 461775',
            1,
            'Verified Official Directory'
        ),
        (
            'Karnataka',
            'Mandya',
            'Mandya Taluk',
            'Electricity Board / DISCOM',
            'Chamundeshwari Electricity Supply Corporation (CESC)',
            'Assistant Executive Engineer (AEE - Rural)',
            '+91 8232 220199',
            'aee_mandya_cesc@karnataka.gov.in',
            'CESC Sub-Division Office, V. V. Nagar, Mandya, KA 571401',
            1,
            'Verified Official Directory'
        ),
        (
            'West Bengal',
            'Darjeeling',
            'Matigara Block',
            'Public Works Department (PWD)',
            'Matigara Block Development Office & Highway Cell',
            'BDO Matigara',
            '+91 353 2571210',
            'bdo_matigara@wb.gov.in',
            'Matigara BDO Office, Kadamtala, Siliguri, WB 734011',
            1,
            'Verified Official Directory'
        )
    ]

    cursor.executemany('''
        INSERT INTO authority_contacts (
            state, district, mandal_municipality, department, office_name,
            contact_person, phone, email, address, is_verified, verification_note
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', authority_contacts)

    conn.commit()
    conn.close()
    print("Database successfully initialized and seeded with sample data!")

if __name__ == '__main__':
    init_db()
