USE food_delivery;

INSERT IGNORE INTO users (full_name, email, phone, password, role) VALUES
('Administrator', 'admin@example.com', '9800000000', CONCAT('sha256$', SHA2('admin123', 256)), 'admin'),
('Sample Customer', 'customer@example.com', '9811111111', CONCAT('sha256$', SHA2('customer123', 256)), 'customer'),
('Sample Rider', 'rider@example.com', '9822222222', CONCAT('sha256$', SHA2('rider123', 256)), 'delivery_person');

INSERT INTO foods (name, description, category, price, image) VALUES
('Classic Burger', 'Grilled vegetable patty, lettuce, tomato, and house sauce.', 'Burger', 250.00, '🍔'),
('Margherita Pizza', 'Cheesy pizza with tomato sauce and fresh basil.', 'Pizza', 450.00, '🍕'),
('Chicken Momo', 'Steamed dumplings served with spicy tomato chutney.', 'Momo', 180.00, '🥟'),
('Veg Chowmein', 'Stir-fried noodles with seasonal vegetables.', 'Noodles', 160.00, '🍜'),
('Chicken Biryani', 'Fragrant rice with tender chicken and aromatic spices.', 'Rice', 320.00, '🍛'),
('Caesar Salad', 'Fresh lettuce, croutons, cheese, and creamy dressing.', 'Salad', 220.00, '🥗'),
('French Fries', 'Crispy golden potato fries with ketchup.', 'Snacks', 120.00, '🍟'),
('Paneer Wrap', 'Spiced paneer and crunchy vegetables in a soft wrap.', 'Wrap', 200.00, '🌯'),
('Chocolate Cake', 'Rich chocolate cake with a soft, moist center.', 'Dessert', 150.00, '🍰'),
('Cold Coffee', 'Chilled coffee blended with milk and ice cream.', 'Beverage', 130.00, '🥤');



USE food_delivery;

DELETE FROM users;

INSERT INTO users (full_name, email, phone, password, role) VALUES
(
    'Administrator',
    'admin@example.com',
    '9800000000',
    'PASTE_ADMIN_HASH_HERE',
    'admin'
),
(
    'Sample Customer',
    'customer@example.com',
    '9811111111',
    'PASTE_CUSTOMER_HASH_HERE',
    'customer'
);

INSERT INTO foods (name, description, category, price, image) VALUES
('Classic Burger', 'Grilled vegetable patty, lettuce, tomato, and house sauce.', 'Burger', 250.00, '🍔'),
('Margherita Pizza', 'Cheesy pizza with tomato sauce and fresh basil.', 'Pizza', 450.00, '🍕'),
('Chicken Momo', 'Steamed dumplings served with spicy tomato chutney.', 'Momo', 180.00, '🥟'),
('Veg Chowmein', 'Stir-fried noodles with seasonal vegetables.', 'Noodles', 160.00, '🍜'),
('Chicken Biryani', 'Fragrant rice with tender chicken and aromatic spices.', 'Rice', 320.00, '🍛'),
('Caesar Salad', 'Fresh lettuce, croutons, cheese, and creamy dressing.', 'Salad', 220.00, '🥗'),
('French Fries', 'Crispy golden potato fries with ketchup.', 'Snacks', 120.00, '🍟'),
('Paneer Wrap', 'Spiced paneer and crunchy vegetables in a soft wrap.', 'Wrap', 200.00, '🌯'),
('Chocolate Cake', 'Rich chocolate cake with a soft, moist center.', 'Dessert', 150.00, '🍰'),
('Cold Coffee', 'Chilled coffee blended with milk and ice cream.', 'Beverage', 130.00, '🥤');
