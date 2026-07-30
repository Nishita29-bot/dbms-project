USE food_delivery;

INSERT IGNORE INTO users (full_name, email, phone, password, role) VALUES
('Administrator', 'admin@example.com', '9800000000', 'admin123', 'admin'),
('Sample Customer', 'customer@example.com', '9811111111', 'customer123', 'customer');

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
