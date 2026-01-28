# Updated for deployment
#!/usr/bin/env python3
"""
Bid Monitor Web Application - Backend API
Flask server that connects the Python bot to the web dashboard
Provides REST API endpoints for the frontend
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime, timedelta
import threading
import time
import os
import sys

# Import the bot
sys.path.append('/home/user')
from bid_monitor_bot import BidMonitorBot

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)  # Enable CORS for frontend

# Database configuration
DB_PATH = '/mnt/user-data/outputs/bids.db'

class BidDatabase:
    """Database manager for bid opportunities"""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create bids table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bid_number TEXT UNIQUE,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                location TEXT NOT NULL,
                type TEXT NOT NULL,
                url TEXT NOT NULL,
                description TEXT,
                posted_date TEXT,
                deadline TEXT,
                keywords TEXT,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                is_favorited INTEGER DEFAULT 0
            )
        ''')
        
        # Create monitoring log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS monitoring_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                opportunities_found INTEGER,
                new_opportunities INTEGER,
                status TEXT,
                error_message TEXT
            )
        ''')
        
        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database initialized: {self.db_path}")
    
    def add_bid(self, bid_data):
        """Add or update a bid opportunity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Extract keywords from title and description
            keywords = self._extract_keywords(bid_data)
            
            cursor.execute('''
                INSERT INTO bids (
                    bid_number, title, source, location, type, url,
                    description, posted_date, deadline, keywords
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(bid_number) DO UPDATE SET
                    title=excluded.title,
                    last_updated=CURRENT_TIMESTAMP,
                    description=excluded.description
            ''', (
                bid_data.get('bid_number', ''),
                bid_data.get('title', ''),
                bid_data.get('source', ''),
                bid_data.get('location', ''),
                bid_data.get('type', ''),
                bid_data.get('url', ''),
                bid_data.get('description', ''),
                bid_data.get('posted_date', ''),
                bid_data.get('deadline', ''),
                keywords
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding bid: {e}")
            return False
        finally:
            conn.close()
    
    def _extract_keywords(self, bid_data):
        """Extract relevant keywords from bid data"""
        keywords = []
        text = f"{bid_data.get('title', '')} {bid_data.get('description', '')}".lower()
        
        keyword_map = {
            'stormwater': ['stormwater', 'storm water', 'drainage'],
            'vac-truck': ['vac truck', 'vacuum truck', 'vactor'],
            'cleaning': ['cleaning', 'sweeping'],
            'sewer': ['sewer', 'sanitary'],
            'maintenance': ['maintenance', 'repair'],
            'catch-basin': ['catch basin', 'storm drain']
        }
        
        for tag, terms in keyword_map.items():
            if any(term in text for term in terms):
                keywords.append(tag)
        
        return ','.join(keywords)
    
    def get_all_bids(self, active_only=True):
        """Get all bids from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM bids"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY posted_date DESC, id DESC"
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_statistics(self):
        """Get bid statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN type = 'Municipal' THEN 1 ELSE 0 END) as municipal,
                SUM(CASE WHEN type = 'County' THEN 1 ELSE 0 END) as county,
                SUM(CASE WHEN type = 'State' THEN 1 ELSE 0 END) as state,
                SUM(CASE WHEN is_favorited = 1 THEN 1 ELSE 0 END) as favorites
            FROM bids WHERE is_active = 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else {}
    
    def toggle_favorite(self, bid_id):
        """Toggle favorite status of a bid"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE bids 
            SET is_favorited = 1 - is_favorited 
            WHERE id = ?
        ''', (bid_id,))
        
        conn.commit()
        conn.close()
        return True
    
    def log_monitoring_run(self, opportunities_found, new_opportunities, status, error_message=None):
        """Log a monitoring run"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO monitoring_log (
                opportunities_found, new_opportunities, status, error_message
            ) VALUES (?, ?, ?, ?)
        ''', (opportunities_found, new_opportunities, status, error_message))
        
        conn.commit()
        conn.close()
    
    def get_last_update(self):
        """Get timestamp of last monitoring run"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT run_timestamp FROM monitoring_log 
            ORDER BY run_timestamp DESC LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return result['run_timestamp'] if result else None

# Initialize database
db = BidDatabase()

# Background monitoring thread
class BidMonitorThread:
    def __init__(self, interval_hours=6):
        self.interval_hours = interval_hours
        self.running = False
        self.thread = None
    
    def start(self):
        """Start background monitoring"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
            print(f"✅ Background monitoring started (every {self.interval_hours} hours)")
    
    def stop(self):
        """Stop background monitoring"""
        self.running = False
        print("⏹️  Background monitoring stopped")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                print(f"\n{'='*60}")
                print(f"🔄 Auto-refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'='*60}\n")
                
                self.run_monitor()
                
                # Sleep for interval
                sleep_seconds = self.interval_hours * 3600
                print(f"\n⏰ Next update in {self.interval_hours} hours")
                time.sleep(sleep_seconds)
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def run_monitor(self):
        """Run the bid monitor and update database"""
        try:
            bot = BidMonitorBot()
            
            # Run monitoring
            bot.scrape_cleveland_city()
            time.sleep(1)
            bot.scrape_cuyahoga_county()
            time.sleep(1)
            bot.scrape_ohio_state()
            time.sleep(1)
            bot.add_sample_opportunities()
            
            # Count existing bids before update
            existing_count = len(db.get_all_bids())
            
            # Update database
            new_count = 0
            for opp in bot.opportunities:
                if db.add_bid(opp):
                    new_count += 1
            
            # Calculate new opportunities
            current_count = len(db.get_all_bids())
            new_opportunities = current_count - existing_count
            
            # Log the run
            db.log_monitoring_run(
                opportunities_found=len(bot.opportunities),
                new_opportunities=new_opportunities,
                status='success'
            )
            
            print(f"✅ Monitoring complete: {len(bot.opportunities)} opportunities")
            print(f"   New: {new_opportunities}, Total in DB: {current_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            db.log_monitoring_run(0, 0, 'error', str(e))
            return False

# Initialize background monitor
monitor_thread = BidMonitorThread(interval_hours=6)

# API Routes

@app.route('/')
def index():
    """Serve the main page"""
    return send_from_directory('static', 'index.html')

@app.route('/api/bids', methods=['GET'])
def get_bids():
    """Get all bid opportunities"""
    try:
        bids = db.get_all_bids()
        return jsonify({
            'success': True,
            'count': len(bids),
            'bids': bids
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get bid statistics"""
    try:
        stats = db.get_statistics()
        last_update = db.get_last_update()
        
        return jsonify({
            'success': True,
            'statistics': stats,
            'last_update': last_update
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/bids/<int:bid_id>/favorite', methods=['POST'])
def toggle_favorite(bid_id):
    """Toggle favorite status of a bid"""
    try:
        db.toggle_favorite(bid_id)
        return jsonify({
            'success': True,
            'message': 'Favorite toggled'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/refresh', methods=['POST'])
def manual_refresh():
    """Manually trigger a monitoring refresh"""
    try:
        success = monitor_thread.run_monitor()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Monitoring refresh completed'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Monitoring refresh failed'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """Export bids to CSV"""
    try:
        import csv
        from io import StringIO
        
        bids = db.get_all_bids()
        
        output = StringIO()
        if bids:
            writer = csv.DictWriter(output, fieldnames=bids[0].keys())
            writer.writeheader()
            writer.writerows(bids)
        
        return app.response_class(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename=bids_{datetime.now().strftime("%Y%m%d")}.csv'}
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'monitoring_active': monitor_thread.running
    })

# Startup
def startup():
    """Initialize application on startup"""
    print("\n" + "="*70)
    print("🚀 BID MONITOR WEB APPLICATION")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run initial monitoring
    print("Running initial monitoring check...")
    monitor_thread.run_monitor()
    
    # Start background monitoring
    monitor_thread.start()
    
    print("\n" + "="*70)
    print("✅ Application ready!")
    print("="*70)
    print()
    print(f"🌐 Web Interface: http://localhost:5000")
    print(f"📊 API Endpoint: http://localhost:5000/api/bids")
    print(f"💾 Database: {DB_PATH}")
    print()
    print("Press Ctrl+C to stop")
    print("="*70 + "\n")

if __name__ == '__main__':
    startup()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
