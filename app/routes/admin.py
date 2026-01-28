import os, uuid
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, jsonify, current_app, Response
)
from flask_login import login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from slugify import slugify
from PIL import Image
import bleach

from app.extensions import db
from app.models.user import User
from app.models.blog import BlogPost

# -----------------------------
# CONFIG
# -----------------------------
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_WIDTH = 1200
JPEG_QUALITY = 80

ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "p", "h1", "h2", "h3", "h4",
    "img", "br", "hr",
    "strong", "em",
    "ul", "ol", "li",
    "blockquote"
]

ALLOWED_ATTRIBUTES = {
    "*": ["style"],
    "img": ["src", "alt"]
}

# -----------------------------
# HELPERS
# -----------------------------
def allowed_file(filename: str):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# -----------------------------
# BLUEPRINT
# -----------------------------
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# -----------------------------
# AUTH
# -----------------------------
@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form["username"]).first()
        if user and user.check_password(request.form["password"]):
            login_user(user)
            return redirect(url_for("admin.dashboard"))
        flash("Credenciales incorrectas", "danger")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))

# -----------------------------
# DASHBOARD
# -----------------------------
@admin_bp.route("/dashboard")
@login_required
def dashboard():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template("admin/dashboard.html", posts=posts)

# -----------------------------
# POSTS
# -----------------------------
@admin_bp.route("/posts/new", methods=["GET", "POST"])
@login_required
def new_post():
    if request.method == "POST":
        title = request.form["title"]

        content = bleach.clean(
            request.form["content"],
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True
        )

        post = BlogPost(
            title=title,
            slug=slugify(title),
            content=content,
            published="published" in request.form
        )

        db.session.add(post)
        db.session.commit()

        flash("Post creado correctamente", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/post_form.html", post=None)


@admin_bp.route("/posts/edit/<int:post_id>", methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    post = BlogPost.query.get_or_404(post_id)

    if request.method == "POST":
        post.title = request.form["title"]
        post.slug = slugify(post.title)

        post.content = bleach.clean(
            request.form["content"],
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True
        )

        post.published = "published" in request.form
        db.session.commit()

        flash("Post actualizado", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/post_form.html", post=post)


@admin_bp.route("/posts/delete/<int:post_id>")
@login_required
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()

    flash("Post eliminado", "warning")
    return redirect(url_for("admin.dashboard"))


# -----------------------------
# CKEDITOR IMAGE UPLOAD
# -----------------------------

@admin_bp.route("/upload-image", methods=["POST"])
@login_required
def upload_image():
    file = request.files.get("upload") or request.files.get("file")
    if not file or file.filename == "":
        return "No file", 400

    if not allowed_file(file.filename):
        return "Invalid file type", 400

    ext = file.filename.rsplit(".", 1)[1].lower()
    base = secure_filename(file.filename.rsplit(".", 1)[0])
    filename = f"{base}-{uuid.uuid4().hex[:8]}.{ext}"

    upload_dir = os.path.join(
        current_app.root_path,
        "static",
        "uploads",
        "blog"
    )
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, filename)

    image = Image.open(file)

    if ext in ("jpg", "jpeg") and image.mode in ("RGBA", "P"):
        image = image.convert("RGB")

    if image.width > MAX_WIDTH:
        ratio = MAX_WIDTH / float(image.width)
        height = int(image.height * ratio)
        image = image.resize((MAX_WIDTH, height), Image.LANCZOS)

    if ext in ("jpg", "jpeg"):
        image.save(file_path, optimize=True, quality=JPEG_QUALITY)
    elif ext == "webp":
        image.save(file_path, quality=80, method=6)
    else:
        image.save(file_path)

    file_url = url_for("static", filename=f"uploads/blog/{filename}")

    # 🔥 RESPUESTA OBLIGATORIA PARA CKEDITOR 4
    func_num = request.args.get("CKEditorFuncNum")
    html = f"""
    <script>
        window.parent.CKEDITOR.tools.callFunction(
            {func_num},
            "{file_url}",
            ""
        );
    </script>
    """
    return Response(html, mimetype="text/html")
