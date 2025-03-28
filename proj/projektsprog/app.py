from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os
from datetime import datetime
from dateutil import parser

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(
    os.path.dirname(__file__), 
    'instance', 
    'sales.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class StockData(db.Model):
    __tablename__ = 'stock_data'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    open_price = db.Column(db.Float, nullable=False)
    high_price = db.Column(db.Float, nullable=False)
    low_price = db.Column(db.Float, nullable=False)
    close_price = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()

def generate_chart(x_data, y_data, chart_type='line', title='', xlabel='', ylabel=''):
    plt.switch_backend('Agg')
    fig, ax = plt.subplots(figsize=(12, 6))
    
    if chart_type == 'line':
        ax.plot(x_data, y_data, color='blue', linewidth=1)
    elif chart_type == 'bar':
        ax.bar(x_data, y_data, color='green', alpha=0.6)
    
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    plt.close(fig)
    img_buffer.seek(0)
    
    return base64.b64encode(img_buffer.read()).decode('utf-8')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    query = request.args.get('query', '').lower().strip()
    
    search_mappings = {
        'visual': url_for('stock_visualizations'),
        'graph': url_for('stock_visualizations'),
        'chart': url_for('stock_visualizations'),
        'raw': url_for('stock_data'),
        'data': url_for('stock_data'),
        'revenue': url_for('stock_data') + '#revenue'
    }

    try:
        parsed_date = parser.parse(query, fuzzy=True)
        return redirect(url_for('stock_data', date=parsed_date.strftime('%Y-%m-%d')))
    except:
        pass

    for keyword, url in search_mappings.items():
        if keyword in query:
            return redirect(url)

    return render_template('search_results.html', 
                         query=query,
                         suggestions=[
                             'Try searching for:',
                             '- "Stock Visualization" for charts',
                             '- "Raw Data" for spreadsheet views',
                             '- Specific dates (e.g., "2023-03-15")',
                             '- "Revenue" for financial metrics'
                         ])

@app.route('/stock-data')
def stock_data():
    data = StockData.query.order_by(StockData.date).all()
    return render_template('stock_data.html', data=data)

@app.route('/stock-visualizations')
def stock_visualizations():
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    start_date = None
    end_date = None
    error = None

    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        error = "Invalid date format. Please use YYYY-MM-DD."

    if not error and start_date and end_date and start_date > end_date:
        error = "Start date must be before end date."

    query = StockData.query.order_by(StockData.date)
    if not error:
        if start_date:
            query = query.filter(StockData.date >= start_date)
        if end_date:
            query = query.filter(StockData.date <= end_date)

    data = query.all() if not error else []

    if error:
        return render_template('stock_visualizations.html',
                            error=error,
                            start_date=start_date_str,
                            end_date=end_date_str), 400
    if not data:
        return render_template('stock_visualizations.html',
                            no_data=True,
                            start_date=start_date_str,
                            end_date=end_date_str)

    dates = [record.date for record in data]
    close_prices = [record.close_price for record in data]
    volumes = [record.volume for record in data]

    date_range = []
    if start_date_str:
        date_range.append(f"from {start_date_str}")
    if end_date_str:
        date_range.append(f"to {end_date_str}")
    
    title_suffix = f" ({' '.join(date_range)})" if date_range else ""
    
    close_title = f'Spotify Stock Closing Prices{title_suffix}'
    volume_title = f'Trading Volume{title_suffix}'

    close_chart = generate_chart(
        dates, close_prices,
        chart_type='line',
        title=close_title,
        xlabel='Date',
        ylabel='Price (USD)'
    )
    
    volume_chart = generate_chart(
        dates, volumes,
        chart_type='bar',
        title=volume_title,
        xlabel='Date',
        ylabel='Volume'
    )

    return render_template(
        'stock_visualizations.html',
        close_price_chart=close_chart,
        volume_chart=volume_chart,
        start_date=start_date_str,
        end_date=end_date_str
    )

if __name__ == '__main__':
    app.run(debug=True)