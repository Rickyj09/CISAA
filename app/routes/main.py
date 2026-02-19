from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from app.models.blog import BlogPost
from flask_mail import Message
from app.extensions import mail
from datetime import datetime

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
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        asunto = request.form.get('asunto', '').strip()
        mensaje = request.form.get('mensaje', '').strip()

        if not nombre or not email or not asunto or not mensaje:
            flash("Todos los campos son obligatorios.", "danger")
            return redirect(url_for("main.contacto"))

        year = datetime.now().year

        try:
            # 1) Email a CISAA (admin)
            msg_admin = Message(
                subject=f"[Web CISAA] {asunto}",
                recipients=["laboratoriocisaa@gmail.com"],
                reply_to=email  # para responder directo al cliente
            )
            msg_admin.html = render_template(
                "emails/contacto_admin.html",
                nombre=nombre, email=email, asunto=asunto, mensaje=mensaje, year=year
            )
            mail.send(msg_admin)

            # 2) Email de confirmación al cliente
            msg_cliente = Message(
                subject="Hemos recibido tu mensaje – CISAA",
                recipients=[email]
            )
            msg_cliente.html = render_template(
                "emails/contacto_cliente.html",
                nombre=nombre, asunto=asunto, year=year
            )
            mail.send(msg_cliente)

            flash("Mensaje enviado correctamente. Nos contactaremos pronto.", "success")

        except Exception as e:
            print("ERROR MAIL:", e)
            flash("Tu mensaje fue recibido, pero no pudimos enviar el correo en este momento. Intentaremos nuevamente.", "warning")

        return redirect(url_for("main.contacto"))

    return render_template('contacto.html')

@main_bp.route("/blog/")
def blog():
    q = (request.args.get("q") or "").strip()

    base = BlogPost.query.filter_by(published=True)

    # 🔎 Búsqueda (ajusta campos si tu modelo no se llama title/content)
    if q:
        base = base.filter(or_(
            BlogPost.title.ilike(f"%{q}%"),
            BlogPost.content.ilike(f"%{q}%")
        ))

    posts = base.order_by(BlogPost.created_at.desc()).all()

    # Sidebar: recientes
    recent_posts = (BlogPost.query
                    .filter_by(published=True)
                    .order_by(BlogPost.created_at.desc())
                    .limit(6)
                    .all())

    # Sidebar: categorías (catálogo fijo por ahora)
    categories = [
        {"label": "Análisis de Suelo", "q": "suelo"},
        {"label": "Calidad de Agua", "q": "agua"},
        {"label": "Análisis Foliar", "q": "foliar"},
        {"label": "Fertilizantes", "q": "fertilizantes"},
        {"label": "Buenas Prácticas", "q": "buenas prácticas"},
    ]

    return render_template(
        "blog.html",
        posts=posts,
        q=q,
        recent_posts=recent_posts,
        categories=categories
    )


@main_bp.route("/blog/<slug>")
def blog_detail(slug):
    post = BlogPost.query.filter_by(slug=slug, published=True).first_or_404()

    # Opcional: sidebar en detalle también (si quieres)
    recent_posts = (BlogPost.query
                    .filter_by(published=True)
                    .order_by(BlogPost.created_at.desc())
                    .limit(6)
                    .all())

    categories = [
        {"label": "Análisis de Suelo", "q": "suelo"},
        {"label": "Calidad de Agua", "q": "agua"},
        {"label": "Análisis Foliar", "q": "foliar"},
        {"label": "Fertilizantes", "q": "fertilizantes"},
        {"label": "Buenas Prácticas", "q": "buenas prácticas"},
    ]

    return render_template("blog_detail.html", post=post, recent_posts=recent_posts, categories=categories)