CREATE TABLE conversation_log (
    id SERIAL PRIMARY KEY,
    transcription TEXT NOT NULL,
    tool VARCHAR(50),
    role VARCHAR(25),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE alarms (
    id SERIAL PRIMARY KEY,
    trigger_time TIMESTAMP,
    timezone VARCHAR(50) NOT NULL,
    status BOOL NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE settings (
    name VARCHAR(50) NOT NULL UNIQUE,
    value TEXT,
    changed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE admin (
    name VARCHAR(50) NOT NULL UNIQUE,
    value TEXT,
    changed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tokens (
    name VARCHAR(50) NOT NULL UNIQUE,
    value JSONB,
    changed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE error_log (
    id SERIAL PRIMARY KEY,
    message TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO settings (name, value) VALUES 
    ('timezone', 'America/New_York'),
    ('language', 'en-US'),
    ('transcription_system', 'openai'),
    ('wake_system', 'charlie'),
    ('wake_word', 'charlie'),
    ('prompt_system', 'openai'),
    ('voice_system', 'openai'),
    ('music_app', 'none'),
    ('volume_levels', 24);

INSERT INTO admin (name, value) VALUES 
    ('spotify_client_id', ''),
    ('spotify_client_secret', ''),
    ('open_api_key', '');
