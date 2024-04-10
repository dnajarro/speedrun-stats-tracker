CREATE TABLE top_ten (
    run_id VARCHAR(50) PRIMARY KEY,
    game_name VARCHAR(50),
    category_id VARCHAR(100),
    category_name VARCHAR(100),
    placement INTEGER,
    player_id1 VARCHAR(50),
    player_name1 VARCHAR(50),
    player_id2 VARCHAR(50),
    player_name2 VARCHAR(50),
    runtime INTEGER,
    verification_date DATE,
    retrieval_date DATE
);

CREATE TABLE all_runs (
    run_id VARCHAR(50) PRIMARY KEY,
    game_name VARCHAR(50),
    category_id VARCHAR(100),
    category_name VARCHAR(100),
    player_id1 VARCHAR(50),
    player_name1 VARCHAR(50),
    player_id2 VARCHAR(50),
    player_name2 VARCHAR(50),
    runtime INTEGER,
    retrieval_date DATE
);

CREATE TABLE ids (
    id VARCHAR(100) PRIMARY KEY,
    speedrun_id VARCHAR(50),
    id_type VARCHAR(50),
    label_name VARCHAR(50)
);