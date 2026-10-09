-- CivicPulse Database Schema (SQLite)

DROP TABLE IF EXISTS reports;
DROP TABLE IF EXISTS authority_contacts;

CREATE TABLE reports (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    image_path TEXT NOT NULL,
    state TEXT NOT NULL,
    district TEXT NOT NULL,
    village_city TEXT NOT NULL,
    mandal_municipality TEXT,
    landmark TEXT,
    latitude REAL,
    longitude REAL,
    observation_date DATE NOT NULL,
    submission_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    severity_level TEXT NOT NULL CHECK(severity_level IN ('Low', 'Medium', 'High', 'Critical')),
    severity_reason TEXT NOT NULL,
    status TEXT DEFAULT 'Reported' CHECK(status IN ('Reported', 'Under Review', 'In Progress', 'Resolved')),
    ai_detected_category TEXT,
    ai_confidence REAL,
    is_sample INTEGER DEFAULT 0,
    upvotes INTEGER DEFAULT 0
);

CREATE TABLE authority_contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state TEXT NOT NULL,
    district TEXT NOT NULL,
    mandal_municipality TEXT,
    department TEXT NOT NULL,
    office_name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    is_verified INTEGER DEFAULT 1,
    verification_note TEXT
);

-- Indexing for performance
CREATE INDEX idx_reports_location ON reports(state, district, village_city);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_category ON reports(category);
CREATE INDEX idx_reports_severity ON reports(severity_level);
CREATE INDEX idx_authority_location ON authority_contacts(state, district, department);
