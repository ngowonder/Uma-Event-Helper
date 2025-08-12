import json
import os
import time
import pyautogui
import re
import tkinter as tk
from tkinter import ttk
from pyautogui import ImageNotFoundException
from utils.screenshot import capture_region
from core.ocr import extract_event_name_text


# Precompile regular expressions for better performance
l_pattern = re.compile(r'l\b')
l_exclamation_pattern = re.compile(r'l([!?.,])')
double_exclamation_pattern = re.compile(r'[!l]{2,}')
trailing_exclamation_pattern = re.compile(r'!+$')
trailing_letter_pattern = re.compile(r'\s+[A-Za-z]\s*$')
trailing_letter_pattern2 = re.compile(r'[A-Za-z]\s*$')


class EventOverlay:
    def __init__(self):
        self.event_region = (243, 201, 365, 45)
        self.overlay_x = 964
        self.overlay_y = 810
        self.overlay_width = 796
        self.overlay_height = 269
        self.support_events = []
        self.uma_events = []
        self.ura_finale_events = []
        self.load_databases()
        self.setup_overlay()
        self.last_event_name = None
        self.event_displayed = False
        self.event_detection_start = None

    def load_databases(self):
        print("Loading event databases...")
        if os.path.exists("assets/events/support_card.json"):
            with open("assets/events/support_card.json", "r", encoding="utf-8-sig") as f:
                self.support_events = json.load(f)
            print(f"   ✓ Loaded {len(self.support_events)} support card events")
        if os.path.exists("assets/events/uma_data.json"):
            with open("assets/events/uma_data.json", "r", encoding="utf-8-sig") as f:
                uma_data = json.load(f)
                for character in uma_data:
                    if "UmaEvents" in character:
                        self.uma_events.extend(character["UmaEvents"])
            print(f"   ✓ Loaded {len(self.uma_events)} uma events")
        if os.path.exists("assets/events/ura_finale.json"):
            with open("assets/events/ura_finale.json", "r", encoding="utf-8-sig") as f:
                self.ura_finale_events = json.load(f)
            print(f"   ✓ Loaded {len(self.ura_finale_events)} ura finale events")
        print("   ✓ Databases loaded successfully")

    def setup_overlay(self):
        self.root = tk.Tk()
        self.root.title("Event Overlay")
        self.root.geometry(f"{self.overlay_width}x{self.overlay_height}+{self.overlay_x}+{self.overlay_y}")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', False)
        self.root.attributes('-alpha', 0.9)
        style = ttk.Style()
        style.theme_use('clam')
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.title_label = ttk.Label(self.main_frame, text="🎮 Event Information", font=('Arial', 14, 'bold'), foreground='#2E86AB')
        self.title_label.pack(pady=(0, 10))
        self.event_name_label = ttk.Label(self.main_frame, text="Waiting for events...", font=('Arial', 12), foreground='#A23B72')
        self.event_name_label.pack(pady=(0, 10))
        self.options_text = tk.Text(self.main_frame, height=8, width=80, font=('Consolas', 10), wrap=tk.WORD, bg='#2C2C2C', fg='#FFFFFF', insertbackground='white', selectbackground='#404040')
        self.options_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.status_label = ttk.Label(self.main_frame, text="🔄 Monitoring for events...", font=('Arial', 10), foreground='#666666')
        self.status_label.pack()
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.options_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.options_text.configure(yscrollcommand=scrollbar.set)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.monitor_events()

    def generate_event_variations(self, event_name):
        event_variations = [event_name]

        if 'l' in event_name:
            variation = l_pattern.sub('!', event_name)
            if variation != event_name and variation not in event_variations:
                event_variations.append(variation)
            variation2 = l_exclamation_pattern.sub(r'!\1', event_name)
            if variation2 != event_name and variation2 not in event_variations:
                event_variations.append(variation2)
        if '!' in event_name:
            variation = event_name.replace('!', 'l')
            if variation not in event_variations:
                event_variations.append(variation)
        if '%' in event_name:
            variation = event_name.replace('%', '☆')
            if variation not in event_variations:
                event_variations.append(variation)
        if '☆' in event_name:
            variation = event_name.replace('☆', '%')
            if variation not in event_variations:
                event_variations.append(variation)
        cleaned_variations = []
        for variation in event_variations:
            cleaned = double_exclamation_pattern.sub('!', variation)
            if cleaned not in event_variations and cleaned != variation:
                cleaned_variations.append(cleaned)
            # Add variation without trailing exclamation marks
            no_exclamation = trailing_exclamation_pattern.sub('', variation).strip()
            if no_exclamation not in event_variations and no_exclamation != variation and no_exclamation:
                cleaned_variations.append(no_exclamation)
            # Add variation without trailing single letters (OCR artifacts)
            no_trailing_letter = trailing_letter_pattern.sub('', variation).strip()
            if no_trailing_letter not in event_variations and no_trailing_letter != variation and no_trailing_letter:
                cleaned_variations.append(no_trailing_letter)
            no_trailing_letter2 = trailing_letter_pattern2.sub('', variation).strip()
            if no_trailing_letter2 not in event_variations and no_trailing_letter2 != variation and no_trailing_letter2:
                cleaned_variations.append(no_trailing_letter2)
        event_variations.extend(cleaned_variations)
        word_order_variations = []
        for variation in event_variations:
            words = variation.split()
            if len(words) >= 3:
                if len(words) == 3:
                    import itertools
                    for perm in itertools.permutations(words):
                        perm_text = ' '.join(perm)
                        if perm_text not in event_variations and perm_text != variation:
                            word_order_variations.append(perm_text)
                elif len(words) == 4:
                    first_half = ' '.join(words[:2])
                    second_half = ' '.join(words[2:])
                    swapped = f"{second_half} {first_half}"
                    if swapped not in event_variations and swapped != variation:
                        word_order_variations.append(swapped)
        event_variations.extend(word_order_variations)
        return event_variations

    def search_events(self, event_variations):
        found_events = {}
        for event in self.support_events:
            db_event_name = event.get("EventName", "").lower()
            clean_db_name = db_event_name.replace("(❯)", "").replace("(❯❯)", "").replace("(❯❯❯)", "").strip()
            for variation in event_variations:
                clean_search_name = variation.lower().strip()
                # Clean search name the same way as database names
                clean_search_name = clean_search_name.replace("(❯)", "").replace("(❯❯)", "").replace("(❯❯❯)", "").strip()
                if clean_db_name == clean_search_name:
                    event_name_key = event['EventName']
                    if event_name_key not in found_events:
                        found_events[event_name_key] = {"source": "Support Card", "options": {}}
                    event_options = event.get("EventOptions", {})
                    for option_name, option_reward in event_options.items():
                        if option_name and any(keyword in option_name.lower() for keyword in ["top option", "bottom option", "middle option", "option1", "option2", "option3"]):
                            found_events[event_name_key]["options"][option_name] = option_reward
                    break
                elif self.fuzzy_match(clean_search_name, clean_db_name) or self.smart_substring_match(clean_search_name, clean_db_name):
                    event_name_key = event['EventName']
                    if event_name_key not in found_events:
                        found_events[event_name_key] = {"source": "Support Card", "options": {}}
                    event_options = event.get("EventOptions", {})
                    for option_name, option_reward in event_options.items():
                        if option_name and any(keyword in option_name.lower() for keyword in ["top option", "bottom option", "middle option", "option1", "option2", "option3"]):
                            found_events[event_name_key]["options"][option_name] = option_reward
                    break
        for event in self.uma_events:
            db_event_name = event.get("EventName", "").lower()
            clean_db_name = db_event_name.replace("(❯)", "").replace("(❯❯)", "").replace("(❯❯❯)", "").strip()
            for variation in event_variations:
                clean_search_name = variation.lower().strip()
                # Clean search name the same way as database names
                clean_search_name = clean_search_name.replace("(❯)", "").replace("(❯❯)", "").replace("(❯❯❯)", "").strip()
                if clean_db_name == clean_search_name:
                    event_name_key = event['EventName']
                    if event_name_key not in found_events:
                        found_events[event_name_key] = {"source": "Uma Data", "options": {}}
                    elif found_events[event_name_key]["source"] == "Support Card":
                        found_events[event_name_key]["source"] = "Both"
                    event_options = event.get("EventOptions", {})
                    for option_name, option_reward in event_options.items():
                        if option_name and any(keyword in option_name.lower() for keyword in ["top option", "bottom option", "middle option", "option1", "option2", "option3"]):
                            found_events[event_name_key]["options"][option_name] = option_reward
                    break
                elif self.fuzzy_match(clean_search_name, clean_db_name) or self.smart_substring_match(clean_search_name, clean_db_name):
                    event_name_key = event['EventName']
                    if event_name_key not in found_events:
                        found_events[event_name_key] = {"source": "Uma Data", "options": {}}
                    elif found_events[event_name_key]["source"] == "Support Card":
                        found_events[event_name_key]["source"] = "Both"
                    event_options = event.get("EventOptions", {})
                    for option_name, option_reward in event_options.items():
                        if option_name and any(keyword in option_name.lower() for keyword in ["top option", "bottom option", "middle option", "option1", "option2", "option3"]):
                            found_events[event_name_key]["options"][option_name] = option_reward
                    break
        for event in self.ura_finale_events:
            db_event_name = event.get("EventName", "").lower()
            clean_db_name = db_event_name.replace("(❯)", "").replace("(❯❯)", "").replace("(❯❯❯)", "").strip()
            for variation in event_variations:
                clean_search_name = variation.lower().strip()
                # Clean search name the same way as database names
                clean_search_name = clean_search_name.replace("(❯)", "").replace("(❯❯)", "").replace("(❯❯❯)", "").strip()
                if clean_db_name == clean_search_name:
                    event_name_key = event['EventName']
                    if event_name_key not in found_events:
                        found_events[event_name_key] = {"source": "Ura Finale", "options": {}}
                    elif found_events[event_name_key]["source"] in ["Support Card", "Uma Data"]:
                        found_events[event_name_key]["source"] = "Multiple Sources"
                    event_options = event.get("EventOptions", {})
                    for option_name, option_reward in event_options.items():
                        if option_name and any(keyword in option_name.lower() for keyword in ["top option", "bottom option", "middle option", "option1", "option2", "option3"]):
                            found_events[event_name_key]["options"][option_name] = option_reward
                    break
                elif self.fuzzy_match(clean_search_name, clean_db_name) or self.smart_substring_match(clean_search_name, clean_db_name):
                    event_name_key = event['EventName']
                    if event_name_key not in found_events:
                        found_events[event_name_key] = {"source": "Ura Finale", "options": {}}
                    elif found_events[event_name_key]["source"] in ["Support Card", "Uma Data"]:
                        found_events[event_name_key]["source"] = "Multiple Sources"
                    event_options = event.get("EventOptions", {})
                    for option_name, option_reward in event_options.items():
                        if option_name and any(keyword in option_name.lower() for keyword in ["top option", "bottom option", "middle option", "option1", "option2", "option3"]):
                            found_events[event_name_key]["options"][option_name] = option_reward
                    break
        return found_events

    def fuzzy_match(self, search_name, db_name):
        common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
        search_words = [word for word in search_name.split() if word not in common_words]
        db_words = [word for word in db_name.split() if word not in common_words]
        if len(search_words) >= 2 and len(db_words) >= 2:
            matches = sum(1 for word in search_words if word in db_words)
            match_ratio = matches / max(len(search_words), len(db_words))
            return match_ratio >= 0.7  # Increased fuzzy match threshold for more precision
        elif len(search_words) == 1 and len(db_words) == 1:
            search_word = search_words[0]
            db_word = db_words[0]
            return search_word in db_word or db_word in search_word
        return False

    def smart_substring_match(self, search_name, db_name):
        """Smart substring matching that prevents short words from matching longer phrases"""
        # If search name is too short, don't match
        if len(search_name) < 8:
            return False
        
        # If search name is a single word and db_name has multiple words, be more careful
        search_words = search_name.split()
        db_words = db_name.split()
        
        if len(search_words) == 1 and len(db_words) > 1:
            # Single word search in multi-word database entry - require longer words
            search_word = search_words[0]
            # Remove punctuation for length check
            clean_word = ''.join(c for c in search_word if c.isalnum())
            if len(clean_word) < 8:
                return False
            # Only match if the search word appears as a complete word in the database entry
            return search_word in db_words
        else:
            # Multi-word search or single-word database entry
            # Be more strict: only allow substring matching if the search name is significantly shorter
            # This prevents "Shrine Visit" from matching "New Year's Shrine Visit"
            if len(search_name) >= len(db_name) * 0.8:  # Search name must be at least 80% of db_name length
                return False
            return search_name in db_name or db_name in search_name

    def update_overlay(self, event_name, found_events):
        if found_events:
            event_name_key = list(found_events.keys())[0]
            self.event_name_label.config(text=f"📋 {event_name_key}")
            self.options_text.delete(1.0, tk.END)
            for event_name_key, event_data in found_events.items():
                self.options_text.insert(tk.END, f"📍 Source: {event_data['source']}\n")
                self.options_text.insert(tk.END, "🎯 Options:\n")
                options = event_data["options"]
                if options:
                    for option_name, option_reward in options.items():
                        reward_single_line = option_reward.replace("\r\n", ", ").replace("\n", ", ").replace("\r", ", ")
                        self.options_text.insert(tk.END, f"   {option_name}: {reward_single_line}\n")
                    option_count = len(options)
                    self.options_text.insert(tk.END, f"\n📊 Total options: {option_count}\n")
                else:
                    self.options_text.insert(tk.END, "   No valid options found\n")
            self.status_label.config(text="✅ Event found!", foreground='#28A745')
        else:
            self.event_name_label.config(text=f"❓ {event_name}")
            self.options_text.delete(1.0, tk.END)
            self.options_text.insert(tk.END, "❌ Unknown event - not found in database\n")
            self.options_text.insert(tk.END, f"Searched for: '{event_name}'\n")
            self.status_label.config(text="❌ Unknown event", foreground='#DC3545')

    def monitor_events(self):
        try:
            try:
                event_icon = pyautogui.locateCenterOnScreen("assets/icons/event_choice_1.png", confidence=0.8, minSearchTime=0.1)
                self.root.lift()
            except ImageNotFoundException:
                event_icon = None
            if event_icon and self.event_detection_start is None:
                self.event_detection_start = time.time()
                self.status_label.config(text="👁️ Event detected, waiting for stability...", foreground='#FFC107')
            if event_icon and self.event_detection_start and not self.event_displayed:
                time_present = time.time() - self.event_detection_start
                if time_present >= 1.0:
                    self.status_label.config(text="✅ Processing event...", foreground='#17A2B8')
                    event_image = capture_region(self.event_region)
                    event_name = extract_event_name_text(event_image)
                    event_name = event_name.strip()
                    if event_name and event_name != self.last_event_name:
                        event_variations = self.generate_event_variations(event_name)
                        found_events = self.search_events(event_variations)
                        self.update_overlay(event_name, found_events)
                        self.last_event_name = event_name
                        self.event_displayed = True
                        self.event_detection_start = None
            elif not event_icon:
                if self.event_displayed:
                    self.event_displayed = False
                    self.last_event_name = None
                    self.status_label.config(text="🔄 Waiting for next event...", foreground='#6C757D')
                elif self.event_detection_start:
                    self.event_detection_start = None
                    self.status_label.config(text="❌ Event disappeared too quickly", foreground='#DC3545')
            self.root.after(500, self.monitor_events)
        except Exception as e:
            self.status_label.config(text=f"❌ Error: {str(e)}", foreground='#DC3545')
            self.root.after(500, self.monitor_events)

    def on_closing(self):
        print("🛑 Event overlay stopped by user")
        self.root.destroy()

    def run(self):
        print("🎮 Event Overlay Started")
        print(f"📍 Overlay position: ({self.overlay_x}, {self.overlay_y})")
        print(f"📏 Overlay size: {self.overlay_width}x{self.overlay_height}")
        print("Press Ctrl+C or close the overlay window to stop")
        print()
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_closing()

def main():
    overlay = EventOverlay()
    overlay.run()

if __name__ == "__main__":
    main() 
