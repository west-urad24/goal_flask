from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy() # sql

# データベース専用
class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 番号 主キー
    description = db.Column(db.String(200), nullable=False) # 目標
    category = db.Column(db.String(50), nullable=False) # 目標の種類
    status = db.Column(db.String(10), nullable=False) # 達成/未達成
    date = db.Column(db.String(50), nullable=False) #いつまでに達成したいか

    def __repr__(self):
        return f"<Goal {self.description}>"
