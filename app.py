from flask import Flask, render_template, redirect, url_for, request
import sqlite3
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


def get_db_connection():
    conn = sqlite3.connect('checklist.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM checklist ORDER BY category, name').fetchall()
    categories = conn.execute('SELECT DISTINCT category FROM checklist ORDER BY category').fetchall()
    locations = conn.execute('SELECT DISTINCT location FROM checklist WHERE location IS NOT NULL AND location != "" ORDER BY location').fetchall()
    conn.close()
    return render_template(
        'checklist.html',
        items=items,
        categories=[row['category'] for row in categories],
        locations=[row['location'] for row in locations]
    )


@app.route('/toggle/<int:item_id>', methods=['POST'])
def toggle(item_id):
    conn = get_db_connection()
    conn.execute('UPDATE checklist SET packed = NOT packed WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/reset', methods=['POST'])
def reset():
    conn = get_db_connection()
    conn.execute('UPDATE checklist SET packed = 0')
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/delete/<int:item_id>', methods=['POST'])
def delete(item_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM checklist WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_item():
    name = request.form.get('name')
    category = request.form.get('category') or 'Uncategorised'
    if name:
        conn = get_db_connection()
        conn.execute(
            'INSERT INTO checklist (name, category, packed) VALUES (?, ?, 0)',
            (name.strip(), category.strip())
        )
        conn.commit()
        conn.close()
    return redirect(url_for('index'))


@app.route('/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    conn = get_db_connection()

    # Get current item
    item = conn.execute('SELECT * FROM checklist WHERE id = ?', (item_id,)).fetchone()

    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category') or 'Uncategorised'
        location = request.form.get('location') or ''
        conn.execute(
            'UPDATE checklist SET name = ?, category = ?, location = ? WHERE id = ?',
            (name.strip(), category.strip(), location.strip(), item_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    # GET method - render edit form
    categories = conn.execute('SELECT DISTINCT category FROM checklist ORDER BY category').fetchall()
    locations = conn.execute('SELECT DISTINCT location FROM checklist WHERE location IS NOT NULL AND location != "" ORDER BY location').fetchall()
    conn.close()
    return render_template(
        'edit_item.html',
        item=item,
        categories=[row['category'] for row in categories],
        locations=[row['location'] for row in locations]
    )


@app.route('/assign-location', methods=['POST'])
def assign_location():
    item_id = request.form.get('id')
    location = request.form.get('location', '')
    conn = get_db_connection()
    conn.execute('UPDATE checklist SET location = ? WHERE id = ?', (location.strip(), item_id))
    conn.commit()
    conn.close()
    return '', 204


if __name__ == '__main__':
    app.run(debug=True)
