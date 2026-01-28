from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import Blueprint, render_template
from app.models.blog import BlogPost

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/quienes-somos')
def quienes_somos():
    return render_template('quienes_somos.html')

@main_bp.route('/servicios')
def servicios():
    return render_template('servicios.html')


# 🔴 ESTA ES LA ÚNICA QUE CAMBIA
@main_bp.route('/contacto', methods=['GET', 'POST'])
def contacto():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        asunto = request.form.get('asunto')
        mensaje = request.form.get('mensaje')

        if not nombre or not email or not mensaje:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('main.contacto'))

        # Aquí luego puedes:
        # - guardar en base de datos
        # - enviar correo
        # - enviar WhatsApp

        flash('Mensaje enviado correctamente. Nos contactaremos contigo.', 'success')
        return redirect(url_for('main.contacto'))

    return render_template('contacto.html')

@main_bp.route("/blog")
def blog():
    posts = BlogPost.query.filter_by(published=True)\
        .order_by(BlogPost.created_at.desc())\
        .all()

    return render_template("blog.html", posts=posts)




@main_bp.route("/blog/<slug>")
def blog_detail(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template("blog_detail.html", post=post)

