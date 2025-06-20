import pytest
from server.models import db, User, Recipe
from server.app import app

@pytest.fixture
def db_session():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

def test_user_creation(db_session):
    user = User(username='testuser', image_url='http://example.com/image.jpg', bio='Test bio')
    user.password_hash = 'testpass'
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
    assert user.username == 'testuser'

def test_username_validation(db_session):
    with pytest.raises(ValueError):
        user = User(username='', image_url='http://example.com/image.jpg')
        db_session.add(user)
        db_session.commit()

def test_password_hash(db_session):
    user = User(username='testuser')
    user.password_hash = 'testpass'
    db_session.add(user)
    db_session.commit()
    assert user.authenticate('testpass')
    assert not user.authenticate('wrongpass')
    with pytest.raises(AttributeError):
        user.password_hash

def test_user_recipes_relationship(db_session):
    user = User(username='testuser')
    user.password_hash = 'testpass'
    db_session.add(user)
    db_session.commit()
    
    recipe1 = Recipe(
        title='Recipe 1',
        instructions='This is a test recipe with more than 50 characters to satisfy the validation requirement.',
        minutes_to_complete=30,
        user_id=user.id
    )
    recipe2 = Recipe(
        title='Recipe 2',
        instructions='Another test recipe with more than 50 characters to satisfy the validation requirement.',
        minutes_to_complete=45,
        user_id=user.id
    )
    db_session.add_all([recipe1, recipe2])
    db_session.commit()
    
    assert len(user.recipes) == 2
    assert user.recipes[0].title == 'Recipe 1'
    assert user.recipes[1].title == 'Recipe 2'