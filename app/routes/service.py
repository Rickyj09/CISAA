from flask import Blueprint, render_template

services_bp = Blueprint(
    "services",
    __name__,
    url_prefix="/servicios"
)

@services_bp.route("/analisis_suelo")
def analisis_suelo():
    return render_template("services/analisis_suelo.html")

@services_bp.route("/analisis_agua")
def analisis_agua():
    return render_template("services/analisis_agua.html")

@services_bp.route("/analisis_foliar")
def analisis_foliar():
    return render_template("services/analisis_foliar.html")

@services_bp.route("/analisis_fertilizantes")
def analisis_fertilizacion():
    return render_template("services/analisis_fertilizantes.html")
