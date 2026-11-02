-- Temporary Google routing coordinates only; never commit returned paths to Git.
CREATE TABLE IF NOT EXISTS citi_route_cache (
 pair_key TEXT PRIMARY KEY,
 coordinates TEXT NOT NULL,
 expires_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS citi_route_cache_expiry ON citi_route_cache(expires_at);
