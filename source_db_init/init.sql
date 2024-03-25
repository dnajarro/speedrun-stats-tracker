CREATE TABLE top_ten (
    run_id VARCHAR(50) PRIMARY KEY,
    player_id1 VARCHAR(50) NOT NULL,
    player_id2 VARCHAR(50),
    category VARCHAR(100),
    game_name VARCHAR(50),
    placement INTEGER,
    runtime INTEGER,
    verification_date DATE,
    retrieval_date DATE
);

CREATE TABLE all_runs (
    run_id VARCHAR(50) PRIMARY KEY,
    player_name1 VARCHAR(50) NOT NULL,
    player_name2 VARCHAR(50),
    category VARCHAR(100),
    game_name VARCHAR(50),
    runtime INTEGER,
    player_id1 VARCHAR(50) NOT NULL,
    player_id2 VARCHAR(50),
    retrieval_date DATE
);

CREATE TABLE ids (
    id VARCHAR(50) PRIMARY KEY,
    id_type VARCHAR(50),
    label_name VARCHAR(50)
);