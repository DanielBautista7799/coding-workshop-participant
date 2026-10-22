-- acme database schema



-- USERS


CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'EMPLOYEE'
        CHECK (role IN ('EMPLOYEE', 'FACILITY_ADMIN', 'ENGINEER')),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CHECK (LOWER(email) LIKE '%@acme.inc')
);


-- FACILITIES
-- Building -> Floor -> Seat

CREATE TABLE IF NOT EXISTS buildings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    address VARCHAR(255)
);


CREATE TABLE IF NOT EXISTS floors (
    id SERIAL PRIMARY KEY,
    building_id INTEGER NOT NULL REFERENCES buildings(id),
    name VARCHAR(50) NOT NULL,

    UNIQUE (building_id, name)
);


CREATE TABLE IF NOT EXISTS seats (
    id SERIAL PRIMARY KEY,
    floor_id INTEGER NOT NULL REFERENCES floors(id),
    label VARCHAR(50) NOT NULL,

    UNIQUE (floor_id, label)
);


-- ENGINEERS


CREATE TABLE IF NOT EXISTS engineer_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    specialty VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);


-- INCIDENTS

CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,

    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,

    priority VARCHAR(20) NOT NULL
        CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH')),

    status VARCHAR(30) NOT NULL DEFAULT 'OPEN'
        CHECK (
            status IN (
                'OPEN',
                'IN_PROGRESS',
                'BLOCKED',
                'RESOLVED',
                'CLOSED'
            )
        ),

    reporter_id INTEGER NOT NULL REFERENCES users(id),
    seat_id INTEGER NOT NULL REFERENCES seats(id),
    engineer_id INTEGER REFERENCES engineer_profiles(id),

    blocked_reason TEXT,

    escalation_status VARCHAR(20) NOT NULL DEFAULT 'NONE'
        CHECK (
            escalation_status IN (
                'NONE',
                'PENDING',
                'APPROVED',
                'DECLINED'
            )
        ),

    escalation_reason TEXT,

    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),

    assigned_at TIMESTAMP,
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    closed_at TIMESTAMP
);


-- TICKET NOTES

CREATE TABLE IF NOT EXISTS ticket_notes (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    author_id INTEGER NOT NULL REFERENCES users(id),
    body TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);


-- STATUS HISTORY

CREATE TABLE IF NOT EXISTS status_history (
    id SERIAL PRIMARY KEY,
    incident_id INTEGER NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
    changed_by_id INTEGER NOT NULL REFERENCES users(id),

    old_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,

    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS skills (
    id SERIAL PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS engineer_skills (
    engineer_id INTEGER NOT NULL
        REFERENCES engineer_profiles(id)
        ON DELETE CASCADE,
    skill_id INTEGER NOT NULL
        REFERENCES skills(id)
        ON DELETE CASCADE,
    PRIMARY KEY (engineer_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_engineer_skills_skill_id
    ON engineer_skills(skill_id);

