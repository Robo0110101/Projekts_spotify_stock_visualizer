from app import app, db, StockData
import pandas as pd
from datetime import datetime
import os

def initialize_database():
    with app.app_context():
        db.drop_all()
        db.create_all()
        print("Database initialized!")

        csv_path = os.path.join(os.path.dirname(__file__), 'spotify_stock_data.csv')
        print(f"Loading data from: {csv_path}")
        
        if not os.path.exists(csv_path):
            print("Error: CSV file not found!")
            return

        try:
            df = pd.read_csv(csv_path)
            print(f"Found {len(df)} records in CSV")

            for index, row in df.iterrows():
                record = StockData(
                    date=datetime.strptime(str(row['date']), '%Y-%m-%d').date(),
                    open_price=float(row['open']),
                    high_price=float(row['high']),
                    low_price=float(row['low']),
                    close_price=float(row['close']),
                    volume=int(row['volume'])
                )
                db.session.add(record)
            
            db.session.commit()
            print(f"Successfully inserted {len(df)} records")
            
        except Exception as e:
            print(f"Error: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    initialize_database()