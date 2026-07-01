from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random

Base = declarative_base()
engine = create_engine('sqlite:///complaints.db', connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(150), unique=True)
    password = Column(String(200))
    role = Column(String(20))  # admin, company, customer

class Complaint(Base):
    __tablename__ = 'complaints'
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    sentiment = Column(String(20))
    confidence = Column(Float)
    polarity = Column(Float)
    source = Column(String(50))   # manual or csv_upload
    institution = Column(String(50))
    user_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(engine)
    session = Session()
    existing = session.query(User).filter_by(email='admin@complaintsense.com').first()
    if not existing:
        session.add(User(
            name='Super Admin',
            email='admin@complaintsense.com',
            password=generate_password_hash('admin123'),
            role='admin'
        ))
        session.add(User(
            name='Vodacom Tanzania',
            email='company@vodacom.com',
            password=generate_password_hash('company123'),
            role='company'
        ))
        session.add(User(
            name='John Mwangi',
            email='customer@gmail.com',
            password=generate_password_hash('customer123'),
            role='customer'
        ))
        session.commit()

        # Sample complaints with varying dates
        from utils.predict import predict_sentiment, detect_institution
        samples = [
            ('Vodacom M-Pesa failed to process my payment and I lost money',),
            ('NMB Bank transfer was fast and seamless, very happy with the service!',),
            ('Tigo Pesa keeps giving me errors when I try to withdraw my cash',),
            ('CRDB mobile app is excellent and very helpful for transfers',),
            ('My Vodacom transaction is pending for 3 days, terrible service',),
            ('Great customer support from NMB Bank, my problem was solved fast',),
            ('The CRDB system was down during my important transfer yesterday',),
            ('Vodacom charges were deducted but transfer did not go through',),
            ('Amazing Tigo Pesa service, best mobile money platform in Tanzania',),
            ('NMB transaction took longer than usual but eventually worked',),
            ('Vodacom M-Pesa agent refused to help me reverse failed transaction',),
            ('CRDB Bank loan application was approved quickly, great experience',),
            ('Tigo Pesa customer care is very rude and unhelpful when I called',),
            ('NMB ATM swallowed my card and nobody helped me for two hours',),
            ('Vodacom data bundles expire too fast, this is a scam!',),
            ('CRDB mobile banking app crashes every time I try to pay bills',),
            ('Tigo Pesa sent money to wrong number and cannot reverse it',),
            ('NMB Bank interest rates are fair and service is professional',),
            ('Vodacom network is always down in Dodoma, very frustrating',),
            ('CRDB Bank staff were very helpful and processed my loan quickly',),
        ]
        base_date = datetime.now() - timedelta(days=60)
        for i, (text,) in enumerate(samples):
            result = predict_sentiment(text)
            institution = detect_institution(text)
            created = base_date + timedelta(days=i*3 + random.randint(0, 2))
            session.add(Complaint(
                text=text,
                sentiment=result['sentiment'],
                confidence=result['confidence'],
                polarity=result.get('polarity', 0.0),
                source='csv_upload',
                institution=institution,
                user_id=1,
                created_at=created
            ))
        session.commit()
    session.close()

def register_user(name, email, password, role):
    session = Session()
    if session.query(User).filter_by(email=email).first():
        session.close()
        return False, 'Email already registered'
    session.add(User(name=name, email=email,
                     password=generate_password_hash(password), role=role))
    session.commit()
    session.close()
    return True, 'Account created successfully'

def login_user(email, password):
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    session.close()
    if user and check_password_hash(user.password, password):
        return True, user
    return False, None

def save_complaint(text, sentiment, confidence, polarity, source, institution, user_id):
    session = Session()
    session.add(Complaint(
        text=text, sentiment=sentiment, confidence=confidence,
        polarity=polarity, source=source, institution=institution,
        user_id=user_id
    ))
    session.commit()
    session.close()

def get_all_complaints():
    session = Session()
    rows = session.query(Complaint).order_by(Complaint.created_at.desc()).all()
    data = [{'id': c.id, 'text': c.text, 'sentiment': c.sentiment,
              'confidence': c.confidence, 'polarity': c.polarity,
              'source': c.source, 'institution': c.institution,
              'user_id': c.user_id, 'created_at': c.created_at} for c in rows]
    session.close()
    return data

def get_user_complaints(user_id):
    session = Session()
    rows = session.query(Complaint).filter_by(user_id=user_id)\
                  .order_by(Complaint.created_at.desc()).all()
    data = [{'id': c.id, 'text': c.text, 'sentiment': c.sentiment,
              'confidence': c.confidence, 'polarity': c.polarity,
              'source': c.source, 'institution': c.institution,
              'created_at': c.created_at} for c in rows]
    session.close()
    return data
