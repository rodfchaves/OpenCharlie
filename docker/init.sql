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
    constant_name VARCHAR(50) NOT NULL UNIQUE,
    value TEXT,
    changed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE admin (
    constant_name VARCHAR(50) NOT NULL UNIQUE,
    value TEXT,
    changed_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE error_log (
    id SERIAL PRIMARY KEY,
    message TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO settings (constant_name, value) VALUES 
    ('timezone', 'America/New_York'),
    ('language', 'en-US'),
    ('transcription_system', 'openai'),
    ('wake_system', 'charlie'),
    ('wake_word', 'charlie'),
    ('prompt_system', 'openai'),
    ('voice_system', 'openai'),
    ('music_app', 'none'),
    ('volume_levels', 24);

INSERT INTO admin (constant_name, value) VALUES 
    ('spotify_client_id', ''),
    ('spotify_client_secret', ''),
    ('open_api_key', '');
