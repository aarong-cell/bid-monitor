#!/usr/bin/env python3
"""
Public Bidding Monitor Bot - Cleveland, Ohio Demo
Monitors government procurement sites for stormwater, vac truck, and cleaning services
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
from datetime import datetime
import re
from typing import List, Dict
import time

class BidMonitorBot:
    def __init__(self):
        self.keywords = [
            'stormwater', 'storm water', 'drainage', 'sewer',
            'vac truck', 'vacuum truck', 'vactor', 'hydro excavation',
            'cleaning', 'street cleaning', 'catch basin', 'storm drain',
            'jetting', 'pipe cleaning', 'sanitary sewer'
        ]
        
        self.opportunities = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def contains_keywords(self, text: str) -> bool:
        """Check if text contains any of our target keywords"""
        if not text:
            return False
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.keywords)
    
    def scrape_cleveland_city(self):
        """Scrape City of Cleveland procurement opportunities"""
        print("🔍 Checking City of Cleveland...")
        
        try:
            # City of Cleveland uses various platforms - checking main procurement page
            url = "https://www.clevelandohio.gov/city-hall/departments/city-finance/purchasing-department"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for bid links and documents
                links = soup.find_all('a', href=True)
                for link in links:
                    link_text = link.get_text(strip=True)
                    href = link['href']
                    
                    if self.contains_keywords(link_text) or self.contains_keywords(href):
                        self.opportunities.append({
                            'source': 'City of Cleveland',
                            'title': link_text[:200],
                            'url': href if href.startswith('http') else f"https://www.clevelandohio.gov{href}",
                            'posted_date': datetime.now().strftime('%Y-%m-%d'),
                            'location': 'Cleveland, OH',
                            'type': 'Municipal'
                        })
                
                print(f"   ✓ Found {len([o for o in self.opportunities if o['source'] == 'City of Cleveland'])} opportunities")
            
        except Exception as e:
            print(f"   ⚠ Error scraping Cleveland: {str(e)}")
    
    def scrape_cuyahoga_county(self):
        """Scrape Cuyahoga County procurement opportunities"""
        print("🔍 Checking Cuyahoga County...")
        
        try:
            # Cuyahoga County procurement portal
            url = "https://cuyahogacounty.us/business/procurement"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find bid opportunities
                content = soup.get_text()
                links = soup.find_all('a', href=True)
                
                for link in links:
                    link_text = link.get_text(strip=True)
                    href = link['href']
                    
                    if self.contains_keywords(link_text):
                        self.opportunities.append({
                            'source': 'Cuyahoga County',
                            'title': link_text[:200],
                            'url': href if href.startswith('http') else f"https://cuyahogacounty.us{href}",
                            'posted_date': datetime.now().strftime('%Y-%m-%d'),
                            'location': 'Cuyahoga County, OH',
                            'type': 'County'
                        })
                
                print(f"   ✓ Found {len([o for o in self.opportunities if o['source'] == 'Cuyahoga County'])} opportunities")
            
        except Exception as e:
            print(f"   ⚠ Error scraping Cuyahoga County: {str(e)}")
    
    def scrape_ohio_state(self):
        """Scrape Ohio State procurement (DAS eProcurement)"""
        print("🔍 Checking Ohio State Procurement...")
        
        try:
            # Ohio's procurement system - checking publicly accessible pages
            url = "https://procure.ohio.gov/Home"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for opportunities
                links = soup.find_all('a', href=True)
                for link in links:
                    link_text = link.get_text(strip=True)
                    href = link['href']
                    
                    if self.contains_keywords(link_text):
                        self.opportunities.append({
                            'source': 'State of Ohio',
                            'title': link_text[:200],
                            'url': href if href.startswith('http') else f"https://procure.ohio.gov{href}",
                            'posted_date': datetime.now().strftime('%Y-%m-%d'),
                            'location': 'Ohio (Statewide)',
                            'type': 'State'
                        })
                
                print(f"   ✓ Found {len([o for o in self.opportunities if o['source'] == 'State of Ohio'])} opportunities")
            
        except Exception as e:
            print(f"   ⚠ Error scraping Ohio State: {str(e)}")
    
    def add_sample_opportunities(self):
        """Add sample opportunities for demo purposes"""
        print("📋 Adding sample opportunities for demonstration...")
        
        samples = [
            {
                'source': 'City of Cleveland',
                'title': 'Storm Sewer Cleaning and CCTV Inspection Services - Annual Contract',
                'url': 'https://www.clevelandohio.gov/city-hall/departments/city-finance/purchasing-department',
                'posted_date': '2026-01-20',
                'deadline': '2026-02-15',
                'location': 'Cleveland, OH',
                'type': 'Municipal',
                'bid_number': 'CLV-2026-0045',
                'description': 'Annual contract for storm sewer cleaning, vac truck services, and CCTV inspection of municipal drainage systems'
            },
            {
                'source': 'Cuyahoga County',
                'title': 'Catch Basin Cleaning and Maintenance Services',
                'url': 'https://cuyahogacounty.us/business/procurement',
                'posted_date': '2026-01-18',
                'deadline': '2026-02-10',
                'location': 'Cuyahoga County, OH',
                'type': 'County',
                'bid_number': 'CC-PW-2026-012',
                'description': 'Countywide catch basin cleaning, storm drain maintenance, and vacuum truck services for stormwater infrastructure'
            },
            {
                'source': 'State of Ohio',
                'title': 'Stormwater Compliance and Drainage System Maintenance',
                'url': 'https://procure.ohio.gov/',
                'posted_date': '2026-01-15',
                'deadline': '2026-02-28',
                'location': 'Region 3 (Northeast Ohio)',
                'type': 'State',
                'bid_number': 'ODOT-SW-2026-089',
                'description': 'ODOT stormwater compliance services including drainage cleaning, vac truck operations, and regulatory reporting'
            },
            {
                'source': 'City of Cleveland',
                'title': 'Sanitary Sewer Jet Cleaning and Hydro Excavation Services',
                'url': 'https://www.clevelandohio.gov/city-hall/departments/city-finance/purchasing-department',
                'posted_date': '2026-01-22',
                'deadline': '2026-02-20',
                'location': 'Cleveland, OH',
                'type': 'Municipal',
                'bid_number': 'CLV-WTR-2026-0078',
                'description': 'Emergency and scheduled sewer cleaning using hydro-jetting and vacuum excavation equipment'
            },
            {
                'source': 'Cuyahoga County',
                'title': 'Street Sweeping and Storm Drain Cleaning - Zone 2',
                'url': 'https://cuyahogacounty.us/business/procurement',
                'posted_date': '2026-01-10',
                'deadline': '2026-02-05',
                'location': 'Cuyahoga County, OH',
                'type': 'County',
                'bid_number': 'CC-ENG-2026-003',
                'description': 'Combined street sweeping and storm drain cleaning services for eastern county municipalities'
            }
        ]
        
        self.opportunities.extend(samples)
        print(f"   ✓ Added {len(samples)} sample opportunities")
    
    def save_to_csv(self, filename: str = 'bid_opportunities.csv'):
        """Save opportunities to CSV file"""
        if not self.opportunities:
            print("⚠ No opportunities to save")
            return
        
        filepath = f"/mnt/user-data/outputs/{filename}"
        
        # Get all unique keys from opportunities
        fieldnames = set()
        for opp in self.opportunities:
            fieldnames.update(opp.keys())
        fieldnames = sorted(list(fieldnames))
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.opportunities)
        
        print(f"💾 Saved {len(self.opportunities)} opportunities to {filepath}")
        return filepath
    
    def save_to_json(self, filename: str = 'bid_opportunities.json'):
        """Save opportunities to JSON file"""
        if not self.opportunities:
            print("⚠ No opportunities to save")
            return
        
        filepath = f"/mnt/user-data/outputs/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.opportunities, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(self.opportunities)} opportunities to {filepath}")
        return filepath
    
    def generate_report(self):
        """Generate a formatted HTML report"""
        if not self.opportunities:
            print("⚠ No opportunities to report")
            return
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Bid Monitoring Report - Cleveland, OH</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            font-size: 32px;
        }}
        .header p {{
            margin: 5px 0;
            opacity: 0.9;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0 0 10px 0;
            color: #667eea;
            font-size: 36px;
        }}
        .stat-card p {{
            margin: 0;
            color: #666;
            font-size: 14px;
        }}
        .opportunity {{
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #667eea;
        }}
        .opportunity h3 {{
            margin: 0 0 15px 0;
            color: #333;
            font-size: 20px;
        }}
        .meta {{
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin-bottom: 15px;
        }}
        .badge {{
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            background-color: #e0e7ff;
            color: #4338ca;
        }}
        .badge.municipal {{
            background-color: #dbeafe;
            color: #1e40af;
        }}
        .badge.county {{
            background-color: #d1fae5;
            color: #065f46;
        }}
        .badge.state {{
            background-color: #fef3c7;
            color: #92400e;
        }}
        .description {{
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        .link {{
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            padding: 10px 20px;
            border: 2px solid #667eea;
            border-radius: 5px;
            transition: all 0.3s;
        }}
        .link:hover {{
            background-color: #667eea;
            color: white;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚛 Public Bidding Opportunities</h1>
        <p><strong>Location:</strong> Cleveland, Ohio & Northeast Ohio Region</p>
        <p><strong>Services:</strong> Stormwater Compliance, Vac Truck Services, Cleaning</p>
        <p><strong>Generated:</strong> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <h3>{len(self.opportunities)}</h3>
            <p>Total Opportunities</p>
        </div>
        <div class="stat-card">
            <h3>{len([o for o in self.opportunities if o['type'] == 'Municipal'])}</h3>
            <p>Municipal Bids</p>
        </div>
        <div class="stat-card">
            <h3>{len([o for o in self.opportunities if o['type'] == 'County'])}</h3>
            <p>County Bids</p>
        </div>
        <div class="stat-card">
            <h3>{len([o for o in self.opportunities if o['type'] == 'State'])}</h3>
            <p>State Bids</p>
        </div>
    </div>
    
    <h2 style="color: #333; margin-bottom: 20px;">📋 Active Opportunities</h2>
"""
        
        for opp in self.opportunities:
            badge_class = opp['type'].lower()
            html_content += f"""
    <div class="opportunity">
        <h3>{opp['title']}</h3>
        <div class="meta">
            <span class="badge {badge_class}">{opp['type']}</span>
            <span class="badge">📍 {opp['location']}</span>
            <span class="badge">📅 Posted: {opp['posted_date']}</span>
            {f"<span class='badge'>⏰ Due: {opp['deadline']}</span>" if 'deadline' in opp else ""}
            {f"<span class='badge'>🔢 {opp['bid_number']}</span>" if 'bid_number' in opp else ""}
        </div>
        {f"<div class='description'>{opp['description']}</div>" if 'description' in opp else ""}
        <div>
            <strong>Source:</strong> {opp['source']}
        </div>
        <div style="margin-top: 15px;">
            <a href="{opp['url']}" class="link" target="_blank">View Opportunity →</a>
        </div>
    </div>
"""
        
        html_content += """
    <div class="footer">
        <p>🤖 Automated Bid Monitoring Bot - Cleveland, Ohio Demo</p>
        <p>This report is automatically generated. Always verify details on official procurement websites.</p>
    </div>
</body>
</html>
"""
        
        filepath = "/mnt/user-data/outputs/bid_report.html"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📊 Generated HTML report: {filepath}")
        return filepath
    
    def run(self):
        """Main execution method"""
        print("=" * 60)
        print("🤖 BID MONITORING BOT - CLEVELAND, OHIO")
        print("=" * 60)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Scrape real sources
        self.scrape_cleveland_city()
        time.sleep(1)  # Be polite to servers
        
        self.scrape_cuyahoga_county()
        time.sleep(1)
        
        self.scrape_ohio_state()
        time.sleep(1)
        
        # Add sample data for demo
        self.add_sample_opportunities()
        
        print()
        print("=" * 60)
        print(f"✅ Monitoring Complete - Found {len(self.opportunities)} opportunities")
        print("=" * 60)
        print()
        
        # Save results
        self.save_to_csv()
        self.save_to_json()
        self.generate_report()
        
        print()
        print("🎉 Demo complete! Check the output files above.")

if __name__ == "__main__":
    bot = BidMonitorBot()
    bot.run()
