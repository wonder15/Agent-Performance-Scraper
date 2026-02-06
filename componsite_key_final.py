import pandas as pd
import os
import re

# --- CONFIGURATION ---
INPUT_FILE_PATH = "/Users/michaelbeaudoin/Downloads/agent_composite_bet_data.csv"
OUTPUT_FILE_PATH = "Categorized_Agent_Bets_Final.xlsx"

# --- KEYWORD DICTIONARY (REFINED) ---
# Uses Regex Boundaries (\b) to match distinct words only.
# Toxic generic keywords (Union, Team, Collection, Shelter, Book, Conservation) have been removed.

CATEGORY_KEYWORDS = {
    # 1. Business
    1: ['business', 'corp', 'corporate', 'merger', 'acquisition', 'startup', 'ceo', 'cfo', 'layoff', 'hiring', 'strike', 'labor union', 'trade union', 'bankruptcy', 'ipo', 'company', 'brand', 'retail', 'supply chain', 'logistics', 'management', 'industry', 'commercial', 'monopoly', 'antitrust', 'executive', 'stellantis', 'byd', 'tesla', 'revenue', 'profit'],

    # 2. Cryptocurrency
    2: ['crypto', 'cryptocurrency', 'bitcoin', 'btc', 'ethereum', 'eth', 'blockchain', 'web3', 'defi', 'nft', 'token', 'wallet', 'coinbase', 'binance', 'solana', 'doge', 'stablecoin', 'altcoin', 'mining', 'ledger', 'satoshi', 'airdrop', 'smart contract', 'bull run'],

    # 3. Politics
    3: ['politics', 'political', 'election', 'vote', 'poll', 'ballot', 'democrat', 'republican', 'congress', 'senate', 'parliament', 'president', 'prime minister', 'biden', 'trump', 'harris', 'campaign', 'legislation', 'bill', 'law', 'supreme court', 'governor', 'mayor', 'tory', 'labour', 'party', 'impeachment', 'regulatory', 'uscis', 'federal court'],

    # 4. Science
    4: ['science', 'physics', 'chemistry', 'biology', 'astronomy', 'nasa', 'space', 'rocket', 'spacex', 'laboratory', 'experiment', 'discovery', 'research', 'scientist', 'nobel prize', 'atom', 'molecule', 'dna', 'genetics', 'telescope', 'quantum', 'fusion', 'superconductor', 'study', 'peer-reviewed', 'comet', 'asteroid'],

    # 5. Technology
    5: ['technology', 'tech', 'ai', 'artificial intelligence', 'gpt', 'llm', 'software', 'hardware', 'app', 'google', 'apple', 'microsoft', 'meta', 'server', 'cloud', 'algorithm', 'robot', 'cyber', 'silicon', 'chip', 'semiconductor', 'nvidia', 'virtual reality', 'metaverse', 'device', 'smartphone', 'adobe', 'semrush'],

    # 6. Trending
    6: ['trending', 'viral', 'trend', 'tiktok', 'meme', 'challenge', 'hashtag', 'breaking', 'hype', 'buzz', 'influencer', 'youtuber', 'streamer', 'mrbeast', 'drama', 'cancel culture'],

    # 7. Fashion
    7: ['fashion', 'clothing', 'apparel', 'brand', 'luxury', 'gucci', 'prada', 'nike', 'adidas', 'sneaker', 'shoe', 'runway', 'designer', 'style', 'vogue', 'wear', 'textile', 'fashion collection', 'couture', 'handbag'],

    # 8. Social
    8: ['social', 'society', 'demographic', 'population', 'census', 'birth rate', 'inequality', 'human rights', 'protest', 'civil rights', 'gender', 'race', 'immigration', 'poverty', 'class', 'community', 'homelessness', 'socio-economic', 'student'],

    # 9. Health
    9: ['health', 'medicine', 'medical', 'doctor', 'hospital', 'virus', 'disease', 'cancer', 'vaccine', 'drug', 'pharmaceutical', 'fda', 'covid', 'pandemic', 'therapy', 'surgery', 'mental health', 'diet', 'nutrition', 'obesity', 'who', 'treatment'],

    # 10. Sustainability
    10: ['sustainability', 'sustainable', 'climate', 'carbon', 'green', 'renewable', 'solar', 'wind', 'energy', 'electric vehicle', 'ev', 'emission', 'pollution', 'environment', 'recycle', 'plastic', 'global warming', 'net zero', 'clean energy'],

    # 11. Internet
    11: ['internet', 'website', 'domain', 'url', 'broadband', 'fiber', 'wifi', '5g', 'browser', 'search engine', 'online', 'digital', 'connectivity', 'network', 'router', 'isp', 'cybersecurity', 'hack', 'ddos'],

    # 12. Travel
    12: ['travel', 'tourism', 'airline', 'flight', 'airport', 'plane', 'boeing', 'airbus', 'hotel', 'resort', 'visa', 'passport', 'destination', 'cruise', 'vacation', 'booking', 'airbnb', 'expedia', 'trip', 'passenger', 'transportation', 'tour', 'bus', 'ntsb'],

    # 13. Food
    13: ['food', 'drink', 'restaurant', 'dining', 'mcdonalds', 'starbucks', 'burger', 'meat', 'plant-based', 'agriculture', 'farming', 'crop', 'harvest', 'beer', 'wine', 'spirit', 'coffee', 'sugar', 'grocery', 'supermarket', 'chef', 'cooking'],

    # 14. Pets
    14: ['pet', 'pets', 'dog', 'cat', 'puppy', 'kitten', 'veterinarian', 'vet', 'breed', 'animal shelter', 'adoption', 'kibble', 'leash', 'domestic animal'],

    # 15. Animals
    15: ['animal', 'wildlife', 'zoo', 'species', 'extinction', 'wildlife conservation', 'nature conservation', 'lion', 'tiger', 'whale', 'bear', 'biodiversity', 'safari', 'jungle', 'forest', 'fauna', 'marine'],

    # 16. Curiosities
    16: ['curiosities', 'mystery', 'ufo', 'alien', 'flat earth', 'paranormal', 'ghost', 'psychic', 'anomaly', 'weird', 'strange', 'guinness', 'record breaker', 'bizarre', 'hoax', 'conspiracy', 'qanon'],

    # 17. Music
    17: ['music', 'song', 'album', 'artist', 'concert', 'tour', 'spotify', 'grammy', 'billboard', 'singer', 'band', 'rapper', 'genre', 'hip hop', 'chart', 'musical', 'vocalist'],

    # 18. Economy
    18: ['economy', 'economic', 'inflation', 'recession', 'gdp', 'cpi', 'interest rate', 'fed', 'federal reserve', 'central bank', 'unemployment', 'jobs report', 'macro', 'debt', 'deficit', 'yield curve', 'treasury', 'fiscal', 'mortgage', 'freddie mac'],

    # 19. Arts
    19: ['art', 'arts', 'museum', 'painting', 'auction', 'sothebys', 'christies', 'gallery', 'masterpiece', 'sculpture', 'artist', 'exhibition', 'cultural', 'literature', 'novel', 'biography', 'author', 'poet'],

    # 20. Entertainment
    20: ['entertainment', 'movie', 'film', 'cinema', 'hollywood', 'actor', 'actress', 'netflix', 'disney', 'hbo', 'box office', 'oscar', 'tv', 'series', 'streaming', 'show', 'theater', 'gambling', 'betting', 'poker', 'casino', 'lottery'],

    # 21. Weather
    21: ['weather', 'forecast', 'hurricane', 'storm', 'tornado', 'temperature', 'rain', 'snow', 'heatwave', 'drought', 'flood', 'meteorology', 'climate', 'monsoon', 'el nino', 'tropical', 'depression', 'dissipate', 'noaa'],

    # 22. Sports
    22: ['sports', 'sport', 'football', 'basketball', 'soccer', 'baseball', 'nfl', 'nba', 'mlb', 'fifa', 'olympics', 'world cup', 'medal', 'champion', 'league', 'sports team', 'athlete', 'score', 'match', 'tournament', 'ufc', 'boxing', 'f1', 'liverpool', 'transfer', 'player', 'tennis', 'grand slam'],

    # 23. Finance
    23: ['finance', 'financial', 'stock', 'share', 'market', 'wall street', 'sp500', 'nasdaq', 'dow jones', 'trade', 'investor', 'dividend', 'portfolio', 'hedge fund', 'equity', 'bond', 'earnings', 'bloomberg', 'etf', 'short', 'long', 'robinhood', 'close'],

    # 24. International
    24: ['international', 'global', 'war', 'conflict', 'ukraine', 'russia', 'israel', 'gaza', 'china', 'un', 'united nations', 'nato', 'treaty', 'diplomacy', 'foreign', 'border', 'geopolitics', 'summit', 'sanction', 'ambassador', 'territory']
}

CATEGORY_NAMES = {
    1: "Business", 2: "Cryptocurrency", 3: "Politics", 4: "Science", 5: "Technology",
    6: "Trending", 7: "Fashion", 8: "Social", 9: "Health", 10: "Sustainability",
    11: "Internet", 12: "Travel", 13: "Food", 14: "Pets", 15: "Animals",
    16: "Curiosities", 17: "Music", 18: "Economy", 19: "Arts", 20: "Entertainment",
    21: "Weather", 22: "Sports", 23: "Finance", 24: "International", 99: "Uncategorized"
}

def categorize_bet(description):
    """
    Categorizes a bet description based on regex word boundaries.
    """
    if not isinstance(description, str):
        return 99
    
    description = description.lower()
    best_category = 99
    max_matches = 0
    
    # Iterate through categories and count keyword matches
    for cat_id, keywords in CATEGORY_KEYWORDS.items():
        matches = 0
        for keyword in keywords:
            # REGEX: \b ensures we match whole words only.
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, description):
                matches += 1
        
        # Tie-breaker: Stick to the category with strictly MORE matches
        if matches > max_matches:
            max_matches = matches
            best_category = cat_id
            
    return best_category

def main():
    print(f"Loading data from: {INPUT_FILE_PATH}...")
    
    try:
        if INPUT_FILE_PATH.endswith('.csv'):
            df = pd.read_csv(INPUT_FILE_PATH)
        else:
            df = pd.read_excel(INPUT_FILE_PATH)
    except FileNotFoundError:
        print("❌ Error: Input file not found. Please check the path.")
        return
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return

    print(f"Successfully loaded {len(df)} rows.")
    
    if 'BET_DESCRIPTION' not in df.columns:
        print("❌ Error: 'BET_DESCRIPTION' column not found.")
        return

    print("Categorizing bets using Regex Boundaries... (This may take ~20 mins for large files)")

    # Apply the categorization logic
    df['CATEGORY_ID'] = df['BET_DESCRIPTION'].apply(categorize_bet)
    
    # FILTER STEP: Remove Uncategorized (99)
    initial_count = len(df)
    df = df[df['CATEGORY_ID'] != 99].copy()
    dropped_count = initial_count - len(df)
    print(f"ℹ️  Dropped {dropped_count} uncategorized bets.")

    # Map Names
    df['CATEGORY_NAME'] = df['CATEGORY_ID'].map(CATEGORY_NAMES)

    # Reorder columns
    cols = ['CATEGORY_ID', 'CATEGORY_NAME'] + [c for c in df.columns if c not in ['CATEGORY_ID', 'CATEGORY_NAME']]
    df = df[cols]

    print(f"Creating Excel file: {OUTPUT_FILE_PATH}...")
    
    try:
        writer = pd.ExcelWriter(OUTPUT_FILE_PATH, engine='xlsxwriter')

        # 1. Master Sheet
        print("  - Writing 'Master_Data' sheet...")
        df.to_excel(writer, sheet_name='Master_Data', index=False)

        # 2. Legend Sheet
        print("  - Writing 'Legend' sheet...")
        legend_data = pd.DataFrame(list(CATEGORY_NAMES.items()), columns=['Category ID', 'Category Name'])
        legend_data = legend_data[legend_data['Category ID'] != 99]
        legend_data.to_excel(writer, sheet_name='Legend', index=False)

        # 3. Category Sheets
        print("  - Writing individual Category sheets...")
        for cat_id, cat_name in CATEGORY_NAMES.items():
            if cat_id == 99: continue
            
            cat_df = df[df['CATEGORY_ID'] == cat_id]
            if not cat_df.empty:
                safe_name = "".join([c for c in cat_name if c not in "[]*:?/\\"])[:30]
                cat_df.to_excel(writer, sheet_name=safe_name, index=False)
                print(f"    -> {safe_name}: {len(cat_df)} rows")

        writer.close()
        print(f"\n✅ Success! File saved to: {os.path.abspath(OUTPUT_FILE_PATH)}")
        
    except Exception as e:
        print(f"❌ Error writing Excel file: {e}")

if __name__ == "__main__":
    main()