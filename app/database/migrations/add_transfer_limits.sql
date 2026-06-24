-- Recreate Transfer Limits Table to include all columns (like monthly_limit)
DROP TABLE IF EXISTS transfer_limits CASCADE;

CREATE TABLE transfer_limits (
    id BIGSERIAL PRIMARY KEY,
    privilege VARCHAR(10) UNIQUE,
    daily_limit NUMERIC(15, 2) NOT NULL DEFAULT 100000.00,
    monthly_limit NUMERIC(15, 2) NOT NULL DEFAULT 1000000.00,
    per_transaction_limit NUMERIC(15, 2) NOT NULL DEFAULT 50000.00,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Default limits by privilege
INSERT INTO transfer_limits (privilege, daily_limit, monthly_limit, per_transaction_limit) VALUES
('SILVER', 50000.00, 500000.00, 25000.00),
('GOLD', 100000.00, 1000000.00, 50000.00),
('PREMIUM', 500000.00, 5000000.00, 200000.00)
ON CONFLICT (privilege) DO NOTHING;

-- Index for faster lookups
CREATE INDEX IF NOT EXISTS idx_transfer_limits_privilege ON transfer_limits(privilege);
