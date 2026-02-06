from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import Blueprint, render_template
from app.models.blog import BlogPost
from flask_mail import Message
from app.extensions import mail


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

        try:
            msg = Message(
                subject=f"[CISAA] {asunto}",
                recipients=["laboratoriocisaa@gmail.com"],
                reply_to=email,
                body=f"""
Nuevo mensaje desde la web CISAA

Nombre: {nombre}
Correo: {email}

Mensaje:
{mensaje}
"""
            )
            mail.send(msg)

            flash("Mensaje enviado correctamente. Nos contactaremos contigo.", "success")

        except Exception as e:
            flash("No se pudo enviar el mensaje. Inténtalo más tarde.", "danger")
            print("ERROR MAIL:", e)

        return redirect(url_for('main.contacto'))

    return render_template('contacto.html')





@main_bp.route("/blog/<slug>")
def blog_detail(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()
    return render_template("blog_detail.html", post=post)

