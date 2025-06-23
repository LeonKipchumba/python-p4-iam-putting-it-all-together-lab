from app import app, db, User, Recipe

with app.app_context():
    db.drop_all()
    db.create_all()

    user1 = User(username='chef1', image_url='https://example.com/chef1.jpg', bio='Loves Italian cuisine')
    user1.password_hash = 'password123'
    user2 = User(username='chef2', image_url='https://example.com/chef2.jpg', bio='Baking enthusiast')
    user2.password_hash = 'password456'

    db.session.add_all([user1, user2])
    db.session.commit()

    recipe1 = Recipe(
        title='Spaghetti Carbonara',
        instructions='Cook spaghetti. Fry pancetta with garlic. Mix eggs and cheese. Combine all with pasta. Serve hot.' * 2,
        minutes_to_complete=30,
        user_id=user1.id
    )
    recipe2 = Recipe(
        title='Chocolate Cake',
        instructions='Mix flour, sugar, cocoa, baking powder. Add eggs, milk, oil. Bake at 350°F for 35 minutes. Frost and serve.' * 2,
        minutes_to_complete=60,
        user_id=user2.id
    )

    db.session.add_all([recipe1, recipe2])
    db.session.commit()

    print("Database seeded successfully!")