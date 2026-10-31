CREATE TABLE IF NOT EXISTS runs (
 activity_id TEXT PRIMARY KEY,
 start_date TEXT NOT NULL,
 local_date TEXT NOT NULL,
 distance_meters REAL NOT NULL CHECK(distance_meters >= 0),
 moving_seconds REAL NOT NULL DEFAULT 0,
 elapsed_seconds REAL NOT NULL DEFAULT 0,
 sport_type TEXT NOT NULL,
 distance_source TEXT NOT NULL,
 has_gps INTEGER NOT NULL CHECK(has_gps IN (0,1)),
 geometry_key TEXT,
 updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS runs_local_date ON runs(local_date);
CREATE INDEX IF NOT EXISTS runs_start_date ON runs(start_date);
CREATE TABLE IF NOT EXISTS dataset_snapshots (
 name TEXT PRIMARY KEY,
 source_sha256 TEXT NOT NULL,
 record_count INTEGER NOT NULL,
 imported_at TEXT NOT NULL
);
