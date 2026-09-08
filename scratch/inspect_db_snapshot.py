import sqlite3

def inspect_db():
    conn = sqlite3.connect('worldnews.db')
    cursor = conn.cursor()

    # SQLite integrity check
    cursor.execute("PRAGMA integrity_check;")
    integrity = cursor.fetchone()[0]
    print(f"PRAGMA integrity_check: {integrity}")

    # Active events count
    cursor.execute("SELECT COUNT(*) FROM events WHERE status = 'active'")
    active_count = cursor.fetchone()[0]

    # Total events count
    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]

    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"Tables in DB: {tables}")

    REGION_MAP = {
        'Africa': ['Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cameroon', 'Central African Republic', 'Chad', 'Comoros', 'Congo', 'DR Congo', 'Djibouti', 'Egypt', 'Equatorial Guinea', 'Eritrea', 'Eswatini', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Ivory Coast', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi', 'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger', 'Nigeria', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles', 'Sierra Leone', 'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Tanzania', 'Togo', 'Tunisia', 'Uganda', 'Zambia', 'Zimbabwe'],
        'Asia': ['Afghanistan', 'Bangladesh', 'Bhutan', 'Brunei', 'Cambodia', 'China', 'India', 'Indonesia', 'Japan', 'Kazakhstan', 'North Korea', 'South Korea', 'Kyrgyzstan', 'Laos', 'Malaysia', 'Maldives', 'Mongolia', 'Myanmar', 'Nepal', 'Pakistan', 'Philippines', 'Singapore', 'Sri Lanka', 'Taiwan', 'Tajikistan', 'Thailand', 'Timor-Leste', 'Turkmenistan', 'Uzbekistan', 'Vietnam'],
        'Europe': ['Albania', 'Andorra', 'Austria', 'Belarus', 'Belgium', 'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary', 'Iceland', 'Ireland', 'Italy', 'Kosovo', 'Latvia', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Malta', 'Moldova', 'Monaco', 'Montenegro', 'Netherlands', 'North Macedonia', 'Norway', 'Poland', 'Portugal', 'Romania', 'Russia', 'San Marino', 'Serbia', 'Slovakia', 'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'Ukraine', 'United Kingdom', 'Vatican City'],
        'Middle East': ['Bahrain', 'Iran', 'Iraq', 'Israel', 'Jordan', 'Kuwait', 'Lebanon', 'Oman', 'Palestine', 'Qatar', 'Saudi Arabia', 'Syria', 'Turkey', 'United Arab Emirates', 'Yemen'],
        'Americas': ['Argentina', 'Bahamas', 'Barbados', 'Belize', 'Bolivia', 'Brazil', 'Canada', 'Chile', 'Colombia', 'Costa Rica', 'Cuba', 'Dominica', 'Dominican Republic', 'Ecuador', 'El Salvador', 'Grenada', 'Guatemala', 'Guyana', 'Haiti', 'Honduras', 'Jamaica', 'Mexico', 'Nicaragua', 'Panama', 'Paraguay', 'Peru', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Suriname', 'Trinidad and Tobago', 'United States', 'Uruguay', 'Venezuela'],
        'Oceania': ['Australia', 'Fiji', 'Kiribati', 'Marshall Islands', 'Micronesia', 'Nauru', 'New Zealand', 'Palau', 'Papua New Guinea', 'Samoa', 'Solomon Islands', 'Tonga', 'Tuvalu', 'Vanuatu']
    }

    def get_region(country, reg_col):
        if reg_col in REGION_MAP:
            return reg_col
        if country:
            for r_name, countries in REGION_MAP.items():
                if country in countries:
                    return r_name
        return 'Unknown'

    cursor.execute("SELECT id, country_name, region, event_type, latitude, longitude FROM events WHERE status = 'active'")
    rows = cursor.fetchall()

    region_counts = {}
    category_counts = {}
    country_counts = {}
    multi_article = 0
    single_article = 0
    unknown_location = 0

    for r in rows:
        eid, country, reg_col, cat, lat, lon = r
        reg = get_region(country, reg_col)
        region_counts[reg] = region_counts.get(reg, 0) + 1
        category_counts[cat or 'Uncategorized'] = category_counts.get(cat or 'Uncategorized', 0) + 1
        country_counts[country or 'Unknown'] = country_counts.get(country or 'Unknown', 0) + 1
        
        # Check article count for event
        if 'event_articles' in tables:
            cursor.execute("SELECT COUNT(*) FROM event_articles WHERE event_id = ?", (eid,))
            art_cnt = cursor.fetchone()[0]
        else:
            art_cnt = 1

        if art_cnt > 1:
            multi_article += 1
        else:
            single_article += 1
            
        if lat is None or lon is None or not country:
            unknown_location += 1

    print(f"Total Active Events: {active_count}")
    print(f"Total Events in DB: {total_events}")
    print(f"Multi-Article Events: {multi_article}")
    print(f"Single-Article Events: {single_article}")
    print(f"Unknown/Unresolved Location: {unknown_location}")
    print("Region Counts:", region_counts)
    print("Category Counts:", category_counts)
    print("Country Counts:", sorted(country_counts.items(), key=lambda x: x[1], reverse=True)[:15])

if __name__ == '__main__':
    inspect_db()

