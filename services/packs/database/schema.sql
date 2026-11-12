CREATE TABLE IF NOT EXISTS packing_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trip_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'other',
    quantity INTEGER NOT NULL DEFAULT 1,
    packed INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'custom'
   
);