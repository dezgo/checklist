from flask import Flask, render_template, redirect, url_for, request
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect('checklist.db')
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM checklist ORDER BY category, name').fetchall()
    categories = conn.execute('SELECT DISTINCT category FROM checklist ORDER BY category').fetchall()
    conn.close()
    return render_template('checklist.html', items=items, categories=[row['category'] for row in categories])


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


if __name__ == '__main__':
    app.run(debug=True)
