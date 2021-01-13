
CREATE TABLE IF NOT EXISTS api_keys
(
    api_key_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    api_key TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP 
)
;

CREATE TABLE IF NOT EXISTS pdfs
(
    pdf_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    ip_address TEXT NOT NULL,
    filename TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    job_id TEXT, 
    enqueued_at DATETIME, 
    processed_at DATETIME
)
;
CREATE TABLE IF NOT EXISTS imgs
(
    img_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    pdf_id INTEGER NOT NULL,
    pdf_page INTEGER, 
    filename TEXT NOT NULL,
    width INTEGER, 
    height INTEGER, 
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
;

insert into api_keys (api_key, status) 
select 'y42WTaddY2pt7m90tqKW', 'active' 
where not exists ( select * from api_keys where api_key = 'y42WTaddY2pt7m90tqKW');

