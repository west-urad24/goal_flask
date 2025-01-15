from flask import Flask, render_template, request, redirect, url_for
from models import db, Goal
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

import matplotlib
matplotlib.use('Agg')
from matplotlib import rcParams

matplotlib.rc('font', family='Hiragino Sans')  # 日本語ラベルが表示されないため追加
rcParams['axes.unicode_minus'] = False

import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///goals.db'
app.config['SECRET_KEY'] = 'mysecret'
app.config['DEBUG'] = False
db.init_app(app)

# htmlフォームの定義
class GoalForm(FlaskForm):
    description = StringField('目標の説明', validators=[DataRequired()])
    category = SelectField('カテゴリ', choices=[('趣味', '趣味'), ('特技', '特技'), ('仕事', '仕事'), ('将来', '将来'), ('美容健康', '美容健康'), ('QOL', 'QOL'), ('性格', '性格'), ('その他', 'その他')], validators=[DataRequired()])
    status = SelectField('達成状況', choices=[('未達成', '未達成'), ('達成', '達成')], validators=[DataRequired()])
    date = StringField('いつまでに？' ,validators=[DataRequired()])
    submit = SubmitField('保存')

# フィルタリング用のフォーム
class FilterForm(FlaskForm):
    category = SelectField('カテゴリ', choices=[('all', 'すべて')] + [('趣味', '趣味'), ('特技', '特技'), ('仕事', '仕事'), ('将来', '将来'), ('美容健康', '美容健康'), ('QOL', 'QOL'), ('性格', '性格'), ('その他', 'その他')], default='all')
    status = SelectField('達成状況', choices=[('all', 'すべて')] + [('未達成', '未達成'), ('達成', '達成')], default='all')
    date = StringField('いつまでに？', default='')
    submit = SubmitField('フィルタ')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = GoalForm()  # 新規目標追加用フォーム
    filter_form = FilterForm()  # フィルタリング用フォーム

    # フィルタリング条件を取得
    category_filter = request.args.get('category', 'all')
    status_filter = request.args.get('status', 'all')
    date_filter = request.args.get('date', '')

    query = Goal.query

    if category_filter != 'all':
        query = query.filter(Goal.category == category_filter)
    if status_filter != 'all':
        query = query.filter(Goal.status == status_filter)
    if date_filter:
        query = query.filter(Goal.date.like(f"%{date_filter}%")) # 任意の文字が含まれていたら

    goals = query.all()

    if form.validate_on_submit():  # 新規目標の追加。保存後、バリデーションがOKならば
        goal = Goal(description=form.description.data, category=form.category.data, status=form.status.data ,date=form.date.data)
        db.session.add(goal)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('main.html', form=form, filter_form=filter_form, goals=goals)

@app.route('/delete/<int:id>')
def delete(id):
    goal = Goal.query.get_or_404(id)  # 番号に一致する目標を削除
    db.session.delete(goal)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    goal = Goal.query.get_or_404(id)  # 番号に一致する目標を編集
    form = GoalForm(obj=goal) # 編集するフォーム
    filter_form = FilterForm()  # フィルタリング用フォーム

    if form.validate_on_submit(): # 保存後、バリデーションがOKならば
        goal.description = form.description.data
        goal.category = form.category.data
        goal.status = form.status.data
        goal.date = form.date.data
        db.session.commit()  # dbに保存
        return redirect(url_for('index'))
    
    # 編集中に全ての目標を表示するためにgoals、フィルタリングのフォーム(フィルタリング中も編集するかもしれないから)、編集中のgoal、フラグのedittingをrender
    return render_template('main.html', form=form, filter_form=filter_form, goals=Goal.query.all(), editing=True, goal=goal)

# グラフ - カテゴリ別の棒グラフを描画
@app.route('/graph')
def graph():
    categories = Goal.query.with_entities(Goal.category, db.func.count(Goal.category)).group_by(Goal.category).all()










    # [[趣味,2],[将来,3]]
    labels = [category[0] for category in categories]
    values = [category[1] for category in categories]
    
    fig, ax = plt.subplots()
    ax.bar(labels, values)

    ax.set_xlabel('カテゴリ')
    ax.set_ylabel('目標数')
    ax.set_title('カテゴリ別の目標数')

    # グラフを画像としてエンコード
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_data = base64.b64encode(img.getvalue()).decode('utf8')
    
    return render_template('graph.html', graph_data=graph_data)

if __name__ == '__main__':
    app.run(debug=True)
