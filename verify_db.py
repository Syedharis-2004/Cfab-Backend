from sqlalchemy import create_engine, text

engine = create_engine('sqlite:///sql_app.db')
with engine.connect() as conn:
    print('--- Database Verification ---')
    print('Users Count:', conn.execute(text('SELECT count(*) FROM users')).scalar())
    print('Assignments Count:', conn.execute(text('SELECT count(*) FROM assignments')).scalar())
    print('Quizzes Count:', conn.execute(text('SELECT count(*) FROM quizzes')).scalar())
    print('User Answers Count:', conn.execute(text('SELECT count(*) FROM user_answers')).scalar())
