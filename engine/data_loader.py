"""
MEMORABLE — Data Loader
Loads and parses narrative JSON files.
"""

import json
import os

def load_scenes() -> dict:
    """Loads all acts into a single flat dict of scene_id -> scene_data"""
    scenes = {}
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'scenes')
    
    files = [
        'act1_awakening.json',
        'act2_descent.json',
        'act3_truth.json'
    ]
    
    for filename in files:
        path = os.path.join(data_dir, filename)
        if not os.path.exists(path):
            continue
            
        with open(path, 'r', encoding='utf-8') as f:
            try:
                act_data = json.load(f)
                if 'scenes' in act_data:
                    for scene_data in act_data['scenes']:
                        scenes[scene_data['id']] = scene_data
                else:
                    # fallback in case some act JSON is a direct dict
                    for scene_id, scene_data in act_data.items():
                        scenes[scene_id] = scene_data
            except Exception as e:
                print(f"[DataLoader] Failed to load {filename}: {e}")
                
    return scenes

def load_characters() -> dict:
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'characters.json')
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return {}
