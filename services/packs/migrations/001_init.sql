CREATE TABLE packing_items (
    id INT IDENTITY(1,1) PRIMARY KEY,
    trip_id INT NOT NULL,
    item_name NVARCHAR(200) NOT NULL,
    category NVARCHAR(200) NOT NULL DEFAULT 'other',
    quantity INT NOT NULL DEFAULT 1,
    packed BIT NOT NULL DEFAULT 0,
    source NVARCHAR(50) NOT NULL DEFAULT 'custom'
   
);