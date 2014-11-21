
from flask import render_template
from app import app



@app.route('/')
def render_planview():
    return render_template('planview.html')

