from flask import Flask, render_template, redirect, url_for,request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os 
from extensions import db


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:aluno@localhost/blog_db'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

db.init_app(app)

from models import User, Post

with app.app_context():
    db.create_all()
    
@app.route('/')
def index():
    posts=Post.query.all()
    return render_template('home.html', posts=posts)

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Conta criada com sucessor!')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password,password):
            session['user_id'] = user.id
            flash('Login bem-sucedido!')
            return redirect(url_for('index'))
        flash('Usuario ou senha incorretos.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Desconectado com sucesso!')
    return redirect(url_for('login'))

@app.route('/post', methods=['GET', 'POST'])
def post():
    if 'user_id' not in session:
        flash('Você precisa estar logado para fazer uma postagem')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files['image']
        
        if image:
            filename=secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_path = filename
        else:
            image_path = None
            
        new_post = Post(title=title, content=content, image=image_path, user_id=session['user_id'])
        db.session.add(new_post)
        db.session.commit()
        flash('Postagem criada com sucesso!')
        return redirect(url_for('index'))
    
    return render_template('post.html')

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    post= Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)

if __name__=='__main__':
    app.run(debug=True)