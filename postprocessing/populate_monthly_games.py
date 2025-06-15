#!/usr/bin/env python3
import json
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# Global variable to store data for saving on interrupt
_data_to_save = None

def signal_handler(sig, frame):
    print('\nCtrl+C detected! Saving processed games and exiting...')
    if _data_to_save:
        with open('games-processed.json', 'w') as f:
            json.dump(_data_to_save, f, indent=2)
        print('Games saved to games-processed.json')
    sys.exit(0)

def generate_link(key):
    # Extract month and year from key like "JUNE 2025 GAMES"
    parts = key.split()
    month = parts[0].lower()
    year = parts[1]
    return f"https://www.humblebundle.com/monthly/p/{month}_{year}_monthly"

class steam_page:
    def __init__(self, game_name):
        self.game_name = game_name
        self.driver = None
    
    def __enter__(self):
        self.driver = webdriver.Chrome()
        self.driver.set_window_size(1280, 720)
        
        try:
            self.driver.get("https://store.steampowered.com/")
            
            # Find search input and search for game
            search_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "store_nav_search_term"))
            )
            search_input.clear()
            search_input.send_keys(self.game_name)
            search_input.send_keys("\n")
            
            time.sleep(2)
            
            # Click the first search result
            title_spans = self.driver.find_elements(By.CSS_SELECTOR, "span.title")
            target_link = None
            
            if title_spans:
                # Get the first search result
                target_link = title_spans[0].find_element(By.XPATH, "./ancestor::a")
            
            if target_link:
                # Click the matching game
                target_link.click()
                
                # Check if age verification is needed
                if "agecheck" in self.driver.current_url:
                    # Handle age verification
                    age_select = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ageYear"))
                    )
                    age_select.send_keys("1990")
                    
                    view_button = self.driver.find_element(By.ID, "view_product_page_btn")
                    view_button.click()
                
                # Wait for page to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "app_tag"))
                )
        
        except Exception as e:
            print(f"Error navigating to {self.game_name}: {e}")
        
        return self.driver
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()

def get_image(webdriver):
    try:
        img_element = webdriver.find_element(By.CLASS_NAME, "game_header_image_full")
        return img_element.get_attribute("src")
    except (TimeoutException, NoSuchElementException):
        return None

def get_genres(webdriver):
    allowed_genres = {
        "Action", "Adventure", "Fps", "Indie", "Mmo", "Multiplayer", 
        "Puzzle", "Racing", "Retro", "Rpg", "Simulation", "Sports", 
        "Strategy", "Virtual Reality"
    }
    
    try:
        app_tags = webdriver.find_elements(By.CLASS_NAME, "app_tag")
        genres = []
        
        for tag in app_tags:
            tag_text = tag.text.strip()
            for allowed_genre in allowed_genres:
                if tag_text.lower() == allowed_genre.lower():
                    genres.append(allowed_genre)
                    break
        
        return genres
        
    except (TimeoutException, NoSuchElementException):
        return []

def process_game(key, game):
    # Skip processing for unwanted games
    if game['name'] in ['Humble Trove', 'About the Charity']:
        return game
    
    game["link"] = generate_link(key)
    with steam_page(game["name"]) as webdriver:
        game["genres"] = get_genres(webdriver)
        game["image"] = get_image(webdriver)
    return game

def process_game_wrapper(args):
    """Wrapper function for threading"""
    key, game_index, game = args
    try:
        print(f"Processing {game['name']}...")
        processed_game = process_game(key, game)
        return (key, game_index, processed_game)
    except Exception as e:
        print(f"Error processing {game['name']}: {e}")
        return (key, game_index, game)  # Return original game if processing fails

def main():
    global _data_to_save
    
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    with open('games-converted.json', 'r') as f:
        data = json.load(f)
    
    _data_to_save = data
    
    # Collect all games that need processing
    tasks = []
    for key, games in data.items():
        for i, game in enumerate(games):
            if game.get('link') is None or game.get("image") is None:
                tasks.append((key, i, game))
    
    print(f"Processing {len(tasks)} games with 5 threads...")
    
    # Process games in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_task = {executor.submit(process_game_wrapper, task): task for task in tasks}
        
        for future in as_completed(future_to_task):
            key, game_index, processed_game = future.result()
            data[key][game_index] = processed_game
    
    with open('games-processed.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("All games processed successfully!")

if __name__ == "__main__":
    main()
