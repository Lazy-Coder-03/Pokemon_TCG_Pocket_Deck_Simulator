import random
import csv
from collections import Counter
import re
import pandas as pd

# =============================================================================
# Card Data and Deck Parsing
# =============================================================================

# Global dictionary to store card data from the CSV
ALL_CARD_DATA = {}

# Map CSV types to internal types
CARD_TYPE_MAPPING = {
    'Metal': 'pokemon',
    'Dragon': 'pokemon',
    'Fire': 'pokemon',
    'Trainer': 'pokemon',
    'Lightning': 'pokemon',
    'Darkness': 'pokemon',
    'Water': 'pokemon',
    'Grass': 'pokemon',
    'Psychic': 'pokemon',
    'Colorless': 'pokemon',
    'Fighting': 'pokemon'
}

def load_card_data(filename="ALL_SETS.csv"):
    """Loads card data from the provided CSV file into a global dictionary."""
    global ALL_CARD_DATA
    try:
        df = pd.read_csv(filename)
        for _, row in df.iterrows():
            card_key = (
                str(row['card_name']).lower().strip(),
                str(row.get('set_code','')).lower().strip(),
                str(row['card_number']).strip()
            )
            ALL_CARD_DATA[card_key] = {
                'card_type': CARD_TYPE_MAPPING.get(str(row['card_type']).strip(), str(row['card_type']).lower().strip()),
                'pokemon_stage': str(row['pokemon_stage']).strip().lower(),
                'ex': str(row['ex']).strip().lower() == 'yes',
                'card_name': str(row['card_name']).strip().lower(),
                'evolve_from': str(row.get('evolves_from', '')).strip().lower() if pd.notna(row.get('evolves_from', '')) else '',
                'rarity': str(row.get('rarity', '')).strip().lower()
            }
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        return False
    except Exception as e:
        print(f"Error loading card data: {e}")
        return False
    return True

def get_card_info(card_string: str):
    """
    Parses a single card string and returns its properties from the dataset.
    e.g., "Froakie A1 87" -> {'card_type': 'pokemon', 'pokemon_stage': 'basic', 'ex': False}
    """
    parts = re.split(r'(\s+)', card_string.strip())
    name_parts, set_code, card_number = [], None, None
    
    for part in reversed(parts):
        if not part.isspace():
            if re.match(r'^[a-zA-Z0-9-]+\s*$', part) and card_number is None:
                card_number = part.strip()
            elif re.match(r'^[a-zA-Z0-9-]+\s*$', part) and set_code is None:
                set_code = part.strip().lower()
            else:
                name_parts.insert(0, part)
    
    card_name = " ".join(name_parts).strip().lower()
    card_key = (card_name, set_code, card_number)
    card_info = ALL_CARD_DATA.get(card_key)
    
    if card_info:
        return card_info
    
    # Fallback search
    for key, info in ALL_CARD_DATA.items():
        if key[0] == card_name and (key[1] == set_code or set_code is None):
            return info
    
    print(f"Warning: Card '{card_name}' not found in data.")
    return None

def parse_decklist(decklist_text: str):
    """
    Parses the raw decklist text provided by the user into a list of card objects.
    Each object contains the card name and its properties.
    """
    parsed_deck = []
    lines = decklist_text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split()
        if len(parts) < 2:
            continue
        
        try:
            count = int(parts[0])
            card_string = " ".join(parts[1:])
        except ValueError:
            continue
        
        card_info = get_card_info(card_string)
        if card_info:
            for _ in range(count):
                parsed_deck.append({
                    'name': card_info.get('card_name', ''),
                    'type': card_info['card_type'],
                    'stage': card_info['pokemon_stage'],
                    'ex': card_info['ex'],
                    'evolve_from': card_info.get('evolve_from', ''),
                    'rarity': card_info.get('rarity', '')
                })
    if len(parsed_deck) != 20:
        print(f"Warning: Decklist does not contain 20 cards (found {len(parsed_deck)})")
        raise ValueError("Decklist must contain exactly 20 cards.")

    # Check for Stage 2 + Rare Candy but missing basic for evolution
    names_in_deck = set(card['name'] for card in parsed_deck)
    has_rare_candy = any(is_rare_candy(card) for card in parsed_deck)
    for card in parsed_deck:
        if is_stage2(card) and has_rare_candy:
            # Find the ultimate basic ancestor for this stage2
            ancestor = get_evolves_from_chain(card.get('evolve_from', '')) if card.get('evolve_from', '') else card['name']
            if ancestor and ancestor not in names_in_deck:
                print(f"Warning: {card['name']} and Rare Candy are present, but required basic ({ancestor}) for evolution is missing from deck.")
    
    return parsed_deck

# =============================================================================
# Helper Functions
# =============================================================================

def is_basic(card):
    return card.get('type','').strip().lower() == 'pokemon' and card.get('stage','').strip().lower() == 'basic'

def is_important(card):
    return card.get('rarity', '').strip().lower() not in ["one diamond"]

def is_stage1(card):
    return card.get('stage','').strip().lower() == 'stage1'

def is_stage2(card):
    return card.get('stage','').strip().lower() == 'stage2'

def is_supporter(card):
    supporter_names = ["erika","misty","blain","koga","giovanni","brock","sabrina","lt. surge",
                       "budding expeditioner","blue","leaf",
                       "cyrus","team galactic grunt","cynthia","volkner","dawn","mars",
                       "irida","celestic town elder","barry","adaman",
                       "iono","pokemon center lady","red","team rocket grunt",
                       "acerola","illima","kiawe","guzma","lana","sophocles","mallow","lillie",
                       "gladion","looker","lusamine",
                       "hau","penny",
                       "will","lyra","silver","fisher","jasmine","hiker",
                       "whitney","travelling merchant","morty",
                       "professor's research"
                       ]
    return (card.get('type','').strip().lower() == 'trainer' and
            any(s in card.get('name','').lower() for s in supporter_names))

def is_professors_research(card):
    return 'professor\'s research' in card.get('name','').lower()

def is_pokeball(card):
    return 'poké ball' in card.get('name','').lower() or 'poke ball' in card.get('name','').lower()

def is_rare_candy(card):
    return 'rare candy' in card.get('name','').lower()

def is_iono(card):
    return 'iono' in card.get('name','').lower()

def is_legendary_beast_ex(card):
    name_lower = card.get('name','').lower()
    return 'raikou ex' in name_lower or 'entei ex' in name_lower or 'suicune ex' in name_lower

def is_main_attacker(card, precomputed_main_attackers):
    return card['name'] in precomputed_main_attackers

# =============================================================================
# Game Actions
# =============================================================================

def draw_from_deck(deck, hand, n):
    """Draws cards from the deck, respecting hand limit."""
    drawn = 0
    for _ in range(n):
        if deck and len(hand) < 10:
            hand.append(deck.pop(0))
            drawn += 1
        else:
            break
    return drawn

def place_basic_pokemon(hand, active_pokemon, bench, max_bench=3):
    """Places basic Pokemon from hand onto the board. Sets 'just_placed' flag for new placements."""
    placed = []
    # Place one basic in active if empty
    if not active_pokemon:
        for i, card in enumerate(hand):
            if is_basic(card):
                card = hand.pop(i)
                card['just_placed'] = True
                active_pokemon.append(card)
                placed.append(("active", card['name']))
                break
    
    # Place remaining basics on bench
    i = 0
    while i < len(hand) and len(bench) < max_bench:
        if is_basic(hand[i]):
            card = hand.pop(i)
            card['just_placed'] = True
            bench.append(card)
            placed.append(("bench", card['name']))
        else:
            i += 1
    
    return placed

def try_play_supporter(hand, deck, supporter_used):
    """Attempts to play a supporter card, prioritizing Professor's Research."""
    if supporter_used[0]:
        return False, None
    
    # Priority 1: Professor's Research
    for i, card in enumerate(hand):
        if is_professors_research(card):
            hand.pop(i)
            supporter_used[0] = True
            hand_size_before = len(hand)
            cards_drawn = draw_from_deck(deck, hand, 2)
            drawn_cards = hand[hand_size_before:hand_size_before + cards_drawn]
            drawn_names = [c['name'] for c in drawn_cards]
            return True, f"Professor's Research (drew {cards_drawn} cards: {', '.join(drawn_names)})"
    
    # Priority 2: Iono
    for i, card in enumerate(hand):
        if is_iono(card):
            hand.pop(i)
            supporter_used[0] = True
            # Shuffle hand back into deck and draw 5
            hand_size = len(hand)
            deck.extend(hand)
            random.shuffle(deck)
            hand.clear()
            cards_drawn = draw_from_deck(deck, hand, 5)
            drawn_names = [c['name'] for c in hand[:cards_drawn]]
            return True, f"Iono (shuffled {hand_size} cards back, drew {cards_drawn}: {', '.join(drawn_names)})"
    
    # Priority 3: Any other supporter
    for i, card in enumerate(hand):
        if is_supporter(card):
            hand.pop(i)
            supporter_used[0] = True
            return True, card['name']
    
    return False, None

def try_play_pokeball(hand, deck):
    """Attempts to play Poké Ball to search for a basic Pokemon."""
    for i, card in enumerate(hand):
        if is_pokeball(card):
            hand.pop(i)
            # Search for basic in deck
            for j, deck_card in enumerate(deck):
                if is_basic(deck_card):
                    if len(hand) < 10:
                        found_card = deck.pop(j)
                        hand.append(found_card)
                        return True, found_card['name']
                    return True, "hand full"
            return True, "no basics found"
    return False, None

def can_evolve(evo_card, pokemon_in_play):
    """Check if an evolution card can be played."""
    evolve_from = evo_card.get('evolve_from', '')
    if not evolve_from:
        return False
    
    # Special case for Eevee evolutions
    if evolve_from == 'eevee':
        valid_names = ['eevee', 'eevee ex']
    else:
        valid_names = [evolve_from]
    
    return any(p.get('name', '') in valid_names for p in pokemon_in_play)

def try_evolve(hand, active_pokemon, bench, deck, supporter_used, turn):
    """Attempts to evolve Pokemon on the board, prioritizing Rare Candy then Sylveon ex."""
    # Evolution restriction: can only evolve after turn 2
    if turn < 2:
        return False, None

    evolved = False
    pokemon_in_play = active_pokemon + bench
    evolution_msgs = []

    # Clear 'just_placed' flag for Pokémon that were placed in previous turns
    for p in bench:
        if p.get('just_placed', False):
            p['just_placed'] = False
    for p in active_pokemon:
        if p.get('just_placed', False):
            p['just_placed'] = False

    # Priority 1: Rare Candy evolution
    rare_candy_cards = [c for c in hand if is_rare_candy(c)]
    stage2_cards = [c for c in hand if is_stage2(c)]

    if rare_candy_cards and stage2_cards:
        for stage2_card in stage2_cards:
            evolve_from_basic_name = get_evolves_from_chain(stage2_card['evolve_from'])
            target = next((p for p in pokemon_in_play if p['name'] == evolve_from_basic_name), None)
            if target:
                if not target.get('just_placed', False):
                    rare_candy = rare_candy_cards.pop(0)
                    hand.remove(rare_candy)
                    hand.remove(stage2_card)

                    location = "active" if target in active_pokemon else "bench"
                    if target in active_pokemon:
                        active_pokemon.remove(target)
                        active_pokemon.append(stage2_card)
                    else:
                        bench.remove(target)
                        bench.append(stage2_card)

                    evolution_msgs.append(f"{target['name']} -> {stage2_card['name']} with Rare Candy in {location}")
                    evolved = True
                    pokemon_in_play = active_pokemon + bench
                    break
                else:
                    evolution_msgs.append(f"Attempted to evolve {target['name']} with Rare Candy in {location} but failed (just placed this turn)")

    # Priority 2: Sylveon ex evolution
    sylveon_ex_card = next((c for c in hand if c['name'] == 'sylveon ex'), None)
    if sylveon_ex_card:
        eevee_target = next((p for p in pokemon_in_play if (p['name'] == 'eevee' or p['name'] == 'eevee ex')), None)
        if eevee_target:
            if not eevee_target.get('just_placed', False):
                hand.remove(sylveon_ex_card)
                location = "active" if eevee_target in active_pokemon else "bench"
                if eevee_target in active_pokemon:
                    active_pokemon.remove(eevee_target)
                    active_pokemon.append(sylveon_ex_card)
                else:
                    bench.remove(eevee_target)
                    bench.append(sylveon_ex_card)

                evolution_msgs.append(f"{eevee_target['name']} -> {sylveon_ex_card['name']} in {location}")
                cards_drawn = draw_from_deck(deck, hand, 2)
                evolution_msgs.append(f"Sylveon ex drew {cards_drawn} cards")
                evolution_msgs.append(f"Hand after drawing:[{', '.join(c['name'] for c in hand)}]")
                evolved = True
                pokemon_in_play = active_pokemon + bench
            else:
                location = "active" if eevee_target in active_pokemon else "bench"
                evolution_msgs.append(f"Attempted to evolve {eevee_target['name']} to Sylveon ex in {location} but failed (just placed this turn)")

    # Priority 3: Any other regular evolutions
    while True:
        found_evolution = False
        for i, card in enumerate(hand):
            # Skip Sylveon ex since it was handled
            if card['name'] == 'sylveon ex':
                continue

            if (is_stage1(card) or is_stage2(card)) and can_evolve(card, pokemon_in_play):
                evolve_from = card.get('evolve_from', '')
                valid_names = ['eevee', 'eevee ex'] if evolve_from == 'eevee' else [evolve_from]
                for target in pokemon_in_play:
                    if target.get('name', '') in valid_names:
                        if not target.get('just_placed', False):
                            evo_card = hand.pop(i)
                            location = "active" if target in active_pokemon else "bench"
                            if target in active_pokemon:
                                active_pokemon.remove(target)
                                active_pokemon.append(evo_card)
                            else:
                                bench.remove(target)
                                bench.append(evo_card)

                            evolution_msgs.append(f"{target['name']} -> {evo_card['name']} in {location}")
                            evolved = True
                            pokemon_in_play = active_pokemon + bench
                            found_evolution = True
                            break
                        else:
                            location = "active" if target in active_pokemon else "bench"
                            evolution_msgs.append(f"Attempted to evolve {target['name']} to {card['name']} in {location} but failed (just placed this turn)")
                if found_evolution:
                    break
        if not found_evolution:
            break
    return evolved, evolution_msgs

def get_evolves_from_chain(card_name):
    """Find the ultimate basic Pokemon for a given card name."""
    current_name = card_name.lower().strip()
    visited = set()
    
    while current_name and current_name not in visited:
        visited.add(current_name)
        card_info = next((info for key, info in ALL_CARD_DATA.items() if info['card_name'] == current_name), None)
        
        if not card_info:
            break
            
        evolve_from = card_info.get('evolve_from', '').strip()
        if not evolve_from or evolve_from == 'nan':
            return current_name
        
        current_name = evolve_from.lower()
    
    return current_name

def try_switch_legendary_beast(hand, active_pokemon, bench, turn):
    """Try to get a legendary beast into the active position."""
    if any(is_legendary_beast_ex(p) for p in active_pokemon):
        return False, None
    
    # Check if we have a beast on bench
    beast_on_bench = next((p for p in bench if is_legendary_beast_ex(p)), None)
    if beast_on_bench:
        # For simplicity, just force switch on turn 2+
        if turn >= 2:
            current_active = active_pokemon.pop(0) if active_pokemon else None
            active_pokemon.append(beast_on_bench)
            bench.remove(beast_on_bench)
            if current_active:
                bench.append(current_active)
            switch_msg = f"switched {beast_on_bench['name']} to active"
            if current_active:
                switch_msg += f" (moved {current_active['name']} to bench)"
            return True, switch_msg
    
    return False, None

def legendary_beast_end_turn_draw(deck, active_pokemon):
    """Draw 1 card if legendary beast is active."""
    if active_pokemon and is_legendary_beast_ex(active_pokemon[0]):
        if deck:
            return [deck.pop(0)]
    return []

# =============================================================================
# Simulation
# =============================================================================

def ensure_guaranteed_basic_top5(deck):
    """Ensures at least one basic Pokemon is in the top 5 cards."""
    opener = deck[:5]
    if any(is_basic(c) for c in opener):
        return deck
    
    for i in range(5, len(deck)):
        if is_basic(deck[i]):
            j = random.randrange(5)
            deck[i], deck[j] = deck[j], deck[i]
            return deck
    
    return deck

def simulate_one_trial_with_logging(full_deck, precomputed_attackers, max_turns=6, log_details=False):
    """Simulate one game with detailed logging."""
    deck = full_deck[:]
    random.shuffle(deck)
    deck = ensure_guaranteed_basic_top5(deck)
    
    hand = deck[:5]
    deck = deck[5:]
    
    active_pokemon = []
    bench = []
    log = []
    
    if log_details:
        log.append("=== GAME START ===")
        log.append(f"Opening hand: {[c['name'] for c in hand]}")
    
    # Place initial basics
    placed = place_basic_pokemon(hand, active_pokemon, bench)
    if log_details and placed:
        for location, name in placed:
            log.append(f"Placed {name} in {location}")
    
    # Track cards for bricking analysis
    cards_seen = set(c['name'] for c in hand + active_pokemon + bench)
    
    # Cards drawn at end of turn (can't be used until next turn)
    cards_drawn_at_end = []
    for turn in range(1, max_turns + 1):
        if cards_drawn_at_end:
            hand.extend(cards_drawn_at_end)
            if log_details:
                log.append(f"Added end-of-turn cards: {[c['name'] for c in cards_drawn_at_end]}")
                log.append(f"Hand after adding end-of-turn cards: {[c['name'] for c in hand]}")
            cards_drawn_at_end.clear()
        
        if log_details:
            log.append(f"\n--- TURN {turn} ---")
            log.append(f"Hand: {[c['name'] for c in hand]}")
            log.append(f"Active: {[c['name'] for c in active_pokemon]}")
            log.append(f"Bench: {[c['name'] for c in bench]}")
            
        supporter_used = [False]

        # Draw for turn (except turn 1)
        if turn > 1:
            hand_size_before = len(hand)
            drawn = draw_from_deck(deck, hand, 1)
            if log_details and drawn > 0:
                drawn_card = hand[hand_size_before]
                log.append(f"Drew card: {drawn_card['name']}")
        
        # Play basics, supporters, etc.
        while True:
            action_taken = False
            
            # Play supporter (prioritizes Professor's Research)
            played_supporter, supporter_msg = try_play_supporter(hand, deck, supporter_used)
            if played_supporter:
                action_taken = True
                if log_details:
                    log.append(f"Played supporter: {supporter_msg}")
            
            # Place any new basics
            placed = place_basic_pokemon(hand, active_pokemon, bench)
            if placed:
                action_taken = True
                if log_details:
                    for location, name in placed:
                        log.append(f"Placed {name} in {location}")
            cards_seen.update(c['name'] for c in active_pokemon + bench)
            
            # Play Poke Balls
            played_pokeball, pokeball_msg = try_play_pokeball(hand, deck)
            if played_pokeball:
                action_taken = True
                if log_details:
                    log.append(f"Played Poké Ball: {pokeball_msg}")
                cards_seen.update(c['name'] for c in hand)
            
            # Try evolutions (evolution restricted to turn 2+)
            evolved, evolution_msg = try_evolve(hand, active_pokemon, bench, deck, supporter_used, turn)
            if evolved:
                action_taken = True
                if log_details:
                    log.append(f"Evolution: {evolution_msg}")
                cards_seen.update(c['name'] for c in active_pokemon + bench)
            
            # Try to switch legendary beast to active
            switched, switch_msg = try_switch_legendary_beast(hand, active_pokemon, bench, turn)
            if switched:
                action_taken = True
                if log_details:
                    log.append(f"Switch: {switch_msg}")

            if not action_taken:
                break
        
        if log_details and turn < 2 and any(is_stage1(c) or is_stage2(c) for c in hand):
            evos_in_hand = [c['name'] for c in hand if is_stage1(c) or is_stage2(c)]
            log.append(f"Evolution cards in hand (can't use until turn 2): {evos_in_hand}")
        
        # End of turn: Legendary beast draw (can't use until next turn)
        beast_draw = legendary_beast_end_turn_draw(deck, active_pokemon)
        if beast_draw:
            cards_drawn_at_end.extend(beast_draw)
            if log_details:
                log.append(f"Legendary beast end-turn draw: {beast_draw[0]['name']} (available next turn)")

    # --- NEW BRICKING LOGIC START ---
    
    all_pokemon_in_play = active_pokemon + bench
    developed_attackers = [p for p in all_pokemon_in_play if is_main_attacker(p, precomputed_attackers)]
    
    # Get total count of each main attacker in the deck
    attacker_names = set(c['name'] for c in full_deck if is_main_attacker(c, precomputed_attackers))
    total_main_attackers_in_deck = len(attacker_names)

    # Check if a game state is NOT a brick
    is_not_brick = False
    
    required_in_play = 3 if total_main_attackers_in_deck > 3 else max(2, total_main_attackers_in_deck)
    is_not_brick = len(developed_attackers) >= required_in_play

    # Check for the "decking out" condition as a final override
    # not_brick_deck_small = len(deck) < 5

    # Determine if it's a brick based on the new logic
    is_brick = not is_not_brick #and not not_brick_deck_small
    
    # --- NEW BRICKING LOGIC END ---
    
    # Existing key card stuck and no attacker logic (for logging purposes only)
    key_cards = ['professor\'s research']
    key_basics = [c['name'] for c in full_deck if is_basic(c) and is_important(c)]
    deck_counts = Counter(card['name'] for card in full_deck if card['name'] in key_cards or card['name'] in key_basics)
    seen_counts = Counter(name for name in cards_seen if name in deck_counts)
    key_cards_stuck = [name for name, total in deck_counts.items() if seen_counts.get(name, 0) == 0]
    
    required_in_play = 3 if total_main_attackers_in_deck > 3 else max(2, total_main_attackers_in_deck)
    brick_no_attacker = len(developed_attackers) < required_in_play
    brick_key_stuck = len(key_cards_stuck) > 0

    if log_details:
        log.append(f"\n--- FINAL STATE ---")
        log.append(f"Active: {[c['name'] for c in active_pokemon]}")
        log.append(f"Bench: {[c['name'] for c in bench]}")
        log.append(f"Hand: {[c['name'] for c in hand]}")
        log.append(f"Main attackers in play: {[c['name'] for c in developed_attackers]}")
        log.append(f"Total main attackers in deck: {total_main_attackers_in_deck}")
        
        log.append(f"RESULT: {'BRICK' if is_brick else 'OK'}")
        
        if is_brick:
            log.append("  - Bricking condition met:")
            if not is_not_brick:
                if total_main_attackers_in_deck > 3:
                    log.append(f"    - Less than 3 attackers ({len(developed_attackers)}) developed when deck has >3 attackers.")
                else:
                    log.append(f"    - Not all attackers ({len(developed_attackers)} of {total_main_attackers_in_deck}) developed.")
        
        # if not_brick_deck_small and not is_brick:
        #     log.append(f"  - Deck size < 5, NOT a BRICK")
        
        log.append(f"Remaining deck: {[c['name'] for c in deck]}")
        
    return is_brick, brick_no_attacker, brick_key_stuck, log

def simulate_brick_rate_with_examples(full_deck, precomputed_attackers, trials=1000, show_examples=5, maxturns=7):
    """
    Run multiple simulations and show detailed examples of bricked games.
    This version ensures the same trial is used for both stats and example logging.
    """
    total_bricks = 0
    attacker_bricks = 0
    key_card_bricks = 0
    
    # Store example logs to display later
    example_logs = []

    for i in range(trials):
        # Run trial once with logging
        is_brick, brick_attacker, brick_key, log = simulate_one_trial_with_logging(
            full_deck, precomputed_attackers, log_details=True, max_turns=maxturns
        )

        # Count stats
        if is_brick:
            total_bricks += 1
            if brick_attacker:
                attacker_bricks += 1
            if brick_key:
                key_card_bricks += 1

            # Store example logs up to show_examples
            if len(example_logs) < show_examples:
                example_logs.append(log)

    return total_bricks, attacker_bricks, key_card_bricks, trials, example_logs


# =============================================================================
# Main
# =============================================================================

def get_main_attackers_and_evolution_methods(full_deck):
    """
    Identifies all potential main attackers and their evolution methods.
    Adds:
      - All Stage 2 Pokémon
      - All Stage 1 EX Pokémon
      - All Basic EX Pokémon
      - Standalone basics (no evolutions OR no stage2 with rare candy)
    """
    main_attackers = set()
    evolution_methods = {}
    has_rare_candy = any(is_rare_candy(c) for c in full_deck)
    
    # Group Pokémon by their basic ancestor
    evolution_lines = {}
    #for eevee ex
    
    for card in full_deck:
        if card['type'] != 'pokemon':
            continue
        basic_name = get_evolves_from_chain(card.get('evolve_from', '')) if card.get('evolve_from', '') else card['name']
        evolution_lines.setdefault(basic_name, []).append(card)

    # Add all Stage 2, Stage 1 EX, Basic EX
    for cards in evolution_lines.values():
        for card in cards:
            name = card['name']
            if is_stage2(card):
                evolution_methods[name] = 'Stage 2 (via Rare Candy)' if has_rare_candy else 'Stage 2'
                main_attackers.add(name)
            elif is_stage1(card) and card.get('ex', False):
                evolution_methods[name] = 'Stage 1 ex'
                main_attackers.add(name)
            elif is_basic(card) and card.get('ex', False):
                evolution_methods[name] = 'Basic ex'
                main_attackers.add(name)
    

    # Add standalone basics not part of any evolution line (no evolutions in deck)
    # Exclude basics if any card in deck evolves from them
    evolved_from_names = set(c.get('evolve_from','') for c in full_deck if c.get('evolve_from',''))
    # Find all basics that have a stage2 in deck that ultimately evolves from them
    basics_with_stage2_rare_candy = set()
    if has_rare_candy:
        for basic_card in full_deck:
            if is_basic(basic_card):
                basic_name = basic_card['name']
                # Look for any stage2 in deck that ultimately evolves from this basic
                for evo_card in full_deck:
                    if is_stage2(evo_card):
                        ancestor = get_evolves_from_chain(evo_card.get('evolve_from','')) if evo_card.get('evolve_from','') else evo_card['name']
                        if ancestor == basic_name:
                            basics_with_stage2_rare_candy.add(basic_name)
                            break

    for card in full_deck:
        if is_basic(card):
            basic_name = card['name']
            # Only add if no card in deck evolves from this basic and not covered by rare candy + stage2
            if basic_name not in evolved_from_names and basic_name not in basics_with_stage2_rare_candy:
                evolution_methods[basic_name] = 'Basic (standalone)'
                main_attackers.add(basic_name)
    
        
    #stage 1 evos that doesnt have any further evos 
    for cards in evolution_lines.values():
        for card in cards:
            if is_stage1(card) and card["name"] not in card.get('evolve_from', []):
                evolution_methods[card['name']] = 'Stage 1 (standalone)'
                main_attackers.add(card['name'])
    
    if 'eevee ex' in main_attackers:
        main_attackers.discard('eevee ex')

    #remove any basic that have a evolution in the deck even if its stage 1
    for card in full_deck:
        if is_basic(card) and card["name"] in card.get('evolve_from', []):
            evolution_methods[card['name']] = 'Basic (with evolution)'
            main_attackers.discard(card['name'])

    return list(main_attackers), evolution_methods





def main():
    """Main function to load data, parse deck, and run analysis."""
    deck_text = """
2 Froakie A1 87
2 Greninja A1 89
2 Suicune ex A4a 20
1 Arceus ex A2a 71
1 Mantyke A4a 23

2 Cyrus A2 150
2 Professor's Research P-A 7
1 Irida A2a 72
1 Leaf A1a 68
1 Mars A2 155
2 Rare Candy A3 144
2 Poké Ball P-A 5
1 Giant Cape A2 147
"""
    
    if not load_card_data():
        print("Failed to load card data.")
        return
    
    parsed_deck = parse_decklist(deck_text)
    if not parsed_deck:
        print("Failed to parse deck.")
        return
    
    print(f"Parsed deck size: {len(parsed_deck)}")
    card_counts = Counter(card['name'] for card in parsed_deck)
    print("Deck composition:")
    for card, count in card_counts.items():
        print(f"   - {count} {card}")
    
    print("\nCard details:")
    unique_cards = {}
    for card in parsed_deck:
        name = card['name']
        if name not in unique_cards:
            unique_cards[name] = card
    
    for name, card in unique_cards.items():
        evolve_info = f", evolves_from={card['evolve_from']}" if card['evolve_from'] else ""
        print(f"   - {name}: type={card['type']}, stage={card['stage']}, ex={card['ex']}{evolve_info}")

    # Precompute main attackers and evolution methods BEFORE the simulation
    main_attackers, evolution_methods = get_main_attackers_and_evolution_methods(parsed_deck)
    print("\nPrecomputed main attackers and evolution methods:")
    for attacker in main_attackers:
        print(f"   - {attacker}: {evolution_methods.get(attacker, 'N/A')}")

    total_bricks, attacker_bricks, key_card_bricks, trials, example_logs = simulate_brick_rate_with_examples(
        parsed_deck, main_attackers, trials=1000, show_examples=5, maxturns=7
    )
    if not example_logs:
        print("No bricked game examples to show.")
    for i, example in enumerate(example_logs, 1):
        print(f"\n--- BRICKED GAME EXAMPLE #{i} ---")
        for line in example:
            print(line)
            
    print(f"\n--- SIMULATION RESULTS ({trials} trials) ---")
    print(f"Total strict bricks (unplayable hands): {total_bricks} ({total_bricks/trials*100:.2f}%)")
    print(f"Sub-optimal games due to not enough main attackers in play: {attacker_bricks} ({attacker_bricks/trials*100:.2f}%)")
    print(f"   - Of these, caused by key cards not drawn in time: {key_card_bricks} ({key_card_bricks/attacker_bricks*100:.2f}% of sub-optimal games) and ({key_card_bricks/trials*100:.2f}% of all games)")
    print(f"Note: Some sub-optimal situations are temporary and may resolve in later turns.")




if __name__ == "__main__":
    main()