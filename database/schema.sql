CREATE TABLE scanned_resources (
    id SERIAL PRIMARY KEY,
    resource_id VARCHAR(255) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    data JSONB,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    resource_id VARCHAR(255) NOT NULL,
    recommendation_type VARCHAR(100),
    current_cost DECIMAL(10,2),
    potential_savings DECIMAL(10,2),
    priority VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE optimization_actions (
    id SERIAL PRIMARY KEY,
    recommendation_id INTEGER REFERENCES recommendations(id),
    action_type VARCHAR(100),
    executed_at TIMESTAMP,
    status VARCHAR(20),
    result TEXT
);

CREATE INDEX idx_resource_id ON scanned_resources(resource_id);
CREATE INDEX idx_status ON recommendations(status);
