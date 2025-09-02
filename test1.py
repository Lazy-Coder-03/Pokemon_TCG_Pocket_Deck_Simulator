import random
import csv
from collections import Counter
import re
import pandas as pd


class CardData:
    """
    Manages card data loading and retrieval from CSV.
    
    NAMING CONVENTION:
    - 'category' = The broad type of card (pokemon, trainer, energy)
    - 'stage' = Pokemon evolution stage (basic, stage1, stage2) 
    - 'ex' = Whether the Pokemon is an EX variant
    """
    
    def __init__(self):
        self.all_card_data = {}
        self.card_type_mapping = {
            'Metal': 'pokemon', 'Dragon': 'pokemon', 'Fire': 'pokemon',
            'Trainer': 'pokemon', 'Lightning': 'pokemon', 'Darkness': 'pokemon',
            'Water': 'pokemon', 'Grass': 'pokemon', 'Psychic': 'pokemon',
            'Colorless': 'pokemon', 'Fighting': 'pokemon'
        }
    
    def load_from_csv(self, filename="ALL_SETS.csv"):
        """Loads card data from the provided CSV file."""
        try:
            df = pd.read_csv(filename)
            for _, row in df.iterrows():
                card_key = (
                    str(row['card_name']).lower().strip(),
                    str(row.get('set_code', '')).lower().strip(),
                    str(row['card_number']).strip()
                )
                self.all_card_data[card_key] = {
                    'card_category': self.card_type_mapping.get(
                        str(row['card_type']).strip(), 
                        str(row['card_type']).lower().strip()
                    ),
                    'pokemon_stage': str(row['pokemon_stage']).strip().lower(),
                    'ex': str(row['ex']).strip().lower() == 'yes',
                    'card_name': str(row['card_name']).strip().lower(),
                    'evolve_from': str(row.get('evolves_from', '')).strip().lower() 
                                  if pd.notna(row.get('evolves_from', '')) else '',
                    'rarity': str(row.get('rarity', '')).strip().lower()
                }
            return True
        except FileNotFoundError:
            print(f"Error: The file {filename} was not found.")
            return False
        except Exception as e:
            print(f"Error loading card data: {e}")
            return False
    
    def get_card_info(self, card_string: str):
        """Parses a single card string and returns its properties from the dataset."""
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
        card_info = self.all_card_data.get(card_key)
        
        if card_info:
            return card_info
        
        # Fallback search
        for key, info in self.all_card_data.items():
            if key[0] == card_name and (key[1] == set_code or set_code is None):
                return info
        
        print(f"Warning: Card '{card_name}' not found in data.")
        return None


class DeckParser:
    """Handles deck parsing and validation."""
    
    def __init__(self, card_data: CardData):
        self.card_data = card_data
    
    def parse_decklist(self, decklist_text: str):
        """Parses the raw decklist text into a list of card objects."""
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
            
            card_info = self.card_data.get_card_info(card_string)
            if card_info:
                for _ in range(count):
                    parsed_deck.append({
                        'name': card_info.get('card_name', ''),
                        'category': card_info['card_category'],  # pokemon, trainer, energy
                        'stage': card_info['pokemon_stage'],     # basic, stage1, stage2
                        'ex': card_info['ex'],
                        'evolve_from': card_info.get('evolve_from', ''),
                        'rarity': card_info.get('rarity', '')
                    })
        
        if len(parsed_deck) != 20:
            print(f"Warning: Decklist does not contain 20 cards (found {len(parsed_deck)})")
            raise ValueError("Decklist must contain exactly 20 cards.")
        
        self._validate_rare_candy_evolution_lines(parsed_deck)
        return parsed_deck
    
    def _validate_rare_candy_evolution_lines(self, deck):
        """Check for Stage 2 + Rare Candy but missing basic for evolution."""
        names_in_deck = set(card['name'] for card in deck)
        has_rare_candy = any(CardHelpers.is_rare_candy(card) for card in deck)
        
        for card in deck:
            if CardHelpers.is_stage2(card) and has_rare_candy:
                ancestor = EvolutionHelper.get_evolves_from_chain(
                    card.get('evolve_from', ''), self.card_data.all_card_data
                ) if card.get('evolve_from', '') else card['name']
                
                if ancestor and ancestor not in names_in_deck:
                    print(f"Warning: {card['name']} and Rare Candy are present, "
                          f"but required basic ({ancestor}) for evolution is missing from deck.")


class CardHelpers:
    """Static helper methods for card type checking."""
    
    @staticmethod
    def is_basic(card):
        return (card.get('category', '').strip().lower() == 'pokemon' and 
                card.get('stage', '').strip().lower() == 'basic')
    
    @staticmethod
    def is_important(card):
        return card.get('rarity', '').strip().lower() not in ["one diamond"]
    
    @staticmethod
    def is_stage1(card):
        return card.get('stage', '').strip().lower() == 'stage1'
    
    @staticmethod
    def is_stage2(card):
        return card.get('stage', '').strip().lower() == 'stage2'
    
    @staticmethod
    def is_supporter(card):
        supporter_names = [
            "erika", "misty", "blain", "koga", "giovanni", "brock", "sabrina", "lt. surge",
            "budding expeditioner", "blue", "leaf",
            "cyrus", "team galactic grunt", "cynthia", "volkner", "dawn", "mars",
            "irida", "celestic town elder", "barry", "adaman",
            "iono", "pokemon center lady", "red", "team rocket grunt",
            "acerola", "illima", "kiawe", "guzma", "lana", "sophocles", "mallow", "lillie",
            "gladion", "looker", "lusamine",
            "hau", "penny",
            "will", "lyra", "silver", "fisher", "jasmine", "hiker",
            "whitney", "travelling merchant", "morty",
            "professor's research"
        ]
        return (card.get('category', '').strip().lower() == 'trainer' and
                any(s in card.get('name', '').lower() for s in supporter_names))
    
    @staticmethod
    def is_professors_research(card):
        return 'professor\'s research' in card.get('name', '').lower()
    
    @staticmethod
    def is_pokeball(card):
        name = card.get('name', '').lower()
        return 'poké ball' in name or 'poke ball' in name
    
    @staticmethod
    def is_rare_candy(card):
        return 'rare candy' in card.get('name', '').lower()
    
    @staticmethod
    def is_iono(card):
        return 'iono' in card.get('name', '').lower()
    
    @staticmethod
    def is_legendary_beast_ex(card):
        name_lower = card.get('name', '').lower()
        return any(beast in name_lower for beast in ['raikou ex', 'entei ex', 'suicune ex'])
    
    @staticmethod
    def is_main_attacker(card, precomputed_main_attackers):
        return card['name'] in precomputed_main_attackers


class EvolutionHelper:
    """Handles evolution-related logic."""
    
    @staticmethod
    def get_evolves_from_chain(card_name, card_data):
        """Find the ultimate basic Pokemon for a given card name."""
        current_name = card_name.lower().strip()
        visited = set()
        
        while current_name and current_name not in visited:
            visited.add(current_name)
            card_info = next(
                (info for key, info in card_data.items() if info['card_name'] == current_name), 
                None
            )
            
            if not card_info:
                break
                
            evolve_from = card_info.get('evolve_from', '').strip()
            if not evolve_from or evolve_from == 'nan':
                return current_name
            
            current_name = evolve_from.lower()
        
        return current_name
    
    @staticmethod
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


class GameActions:
    """Handles all game actions during simulation."""
    
    @staticmethod
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
    
    @staticmethod
    def place_basic_pokemon(hand, active_pokemon, bench, max_bench=3):
        """Places basic Pokemon from hand onto the board."""
        placed = []
        
        # Place one basic in active if empty
        if not active_pokemon:
            for i, card in enumerate(hand):
                if CardHelpers.is_basic(card):
                    card = hand.pop(i)
                    card['just_placed'] = True
                    active_pokemon.append(card)
                    placed.append(("active", card['name']))
                    break
        
        # Place remaining basics on bench
        i = 0
        while i < len(hand) and len(bench) < max_bench:
            if CardHelpers.is_basic(hand[i]):
                card = hand.pop(i)
                card['just_placed'] = True
                bench.append(card)
                placed.append(("bench", card['name']))
            else:
                i += 1
        
        return placed
    
    @staticmethod
    def try_play_supporter(hand, deck, supporter_used):
        """Attempts to play a supporter card, prioritizing Professor's Research."""
        if supporter_used[0]:
            return False, None
        
        # Priority 1: Professor's Research
        for i, card in enumerate(hand):
            if CardHelpers.is_professors_research(card):
                hand.pop(i)
                supporter_used[0] = True
                hand_size_before = len(hand)
                cards_drawn = GameActions.draw_from_deck(deck, hand, 2)
                drawn_cards = hand[hand_size_before:hand_size_before + cards_drawn]
                drawn_names = [c['name'] for c in drawn_cards]
                return True, f"Professor's Research (drew {cards_drawn} cards: {', '.join(drawn_names)})"
        
        # Priority 2: Iono
        for i, card in enumerate(hand):
            if CardHelpers.is_iono(card):
                hand.pop(i)
                supporter_used[0] = True
                hand_size = len(hand)
                deck.extend(hand)
                random.shuffle(deck)
                hand.clear()
                cards_drawn = GameActions.draw_from_deck(deck, hand, 5)
                drawn_names = [c['name'] for c in hand[:cards_drawn]]
                return True, f"Iono (shuffled {hand_size} cards back, drew {cards_drawn}: {', '.join(drawn_names)})"
        
        # Priority 3: Any other supporter
        for i, card in enumerate(hand):
            if CardHelpers.is_supporter(card):
                hand.pop(i)
                supporter_used[0] = True
                return True, card['name']
        
        return False, None
    
    @staticmethod
    def try_play_pokeball(hand, deck):
        """Attempts to play Poké Ball to search for a basic Pokemon."""
        for i, card in enumerate(hand):
            if CardHelpers.is_pokeball(card):
                hand.pop(i)
                # Search for basic in deck
                for j, deck_card in enumerate(deck):
                    if CardHelpers.is_basic(deck_card):
                        if len(hand) < 10:
                            found_card = deck.pop(j)
                            hand.append(found_card)
                            return True, found_card['name']
                        return True, "hand full"
                return True, "no basics found"
        return False, None


class EvolutionActions:
    """Handles evolution-specific actions."""
    
    @staticmethod
    def try_evolve(hand, active_pokemon, bench, deck, supporter_used, turn, card_data):
        """Attempts to evolve Pokemon on the board."""
        if turn < 2:
            return False, None

        evolved = False
        pokemon_in_play = active_pokemon + bench
        evolution_msgs = []

        # Clear 'just_placed' flag for Pokemon that were placed in previous turns
        for p in bench + active_pokemon:
            if p.get('just_placed', False):
                p['just_placed'] = False

        # Priority 1: Rare Candy evolution
        evolved, evolution_msgs = EvolutionActions._try_rare_candy_evolution(
            hand, pokemon_in_play, active_pokemon, bench, evolved, evolution_msgs, card_data
        )

        # Priority 2: Sylveon ex evolution
        evolved, evolution_msgs = EvolutionActions._try_sylveon_evolution(
            hand, pokemon_in_play, active_pokemon, bench, deck, evolved, evolution_msgs
        )

        # Priority 3: Regular evolutions
        evolved, evolution_msgs = EvolutionActions._try_regular_evolutions(
            hand, pokemon_in_play, active_pokemon, bench, deck, evolved, evolution_msgs
        )

        return evolved, evolution_msgs
    
    @staticmethod
    def _try_rare_candy_evolution(hand, pokemon_in_play, active_pokemon, bench, evolved, evolution_msgs, card_data):
        """Handle Rare Candy evolution logic."""
        rare_candy_cards = [c for c in hand if CardHelpers.is_rare_candy(c)]
        stage2_cards = [c for c in hand if CardHelpers.is_stage2(c)]

        if rare_candy_cards and stage2_cards:
            for stage2_card in stage2_cards:
                evolve_from_basic_name = EvolutionHelper.get_evolves_from_chain(
                    stage2_card['evolve_from'], card_data
                )
                target = next((p for p in pokemon_in_play if p['name'] == evolve_from_basic_name), None)
                
                if target and not target.get('just_placed', False):
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
                    break
                elif target and target.get('just_placed', False):
                    location = "active" if target in active_pokemon else "bench"
                    evolution_msgs.append(f"Attempted to evolve {target['name']} with Rare Candy in {location} but failed (just placed this turn)")
        
        return evolved, evolution_msgs
    
    @staticmethod
    def _try_sylveon_evolution(hand, pokemon_in_play, active_pokemon, bench, deck, evolved, evolution_msgs):
        """Handle Sylveon ex evolution logic."""
        sylveon_ex_card = next((c for c in hand if c['name'] == 'sylveon ex'), None)
        if sylveon_ex_card:
            eevee_target = next((p for p in pokemon_in_play if p['name'] in ['eevee', 'eevee ex']), None)
            if eevee_target and not eevee_target.get('just_placed', False):
                hand.remove(sylveon_ex_card)
                location = "active" if eevee_target in active_pokemon else "bench"
                
                if eevee_target in active_pokemon:
                    active_pokemon.remove(eevee_target)
                    active_pokemon.append(sylveon_ex_card)
                else:
                    bench.remove(eevee_target)
                    bench.append(sylveon_ex_card)

                evolution_msgs.append(f"{eevee_target['name']} -> {sylveon_ex_card['name']} in {location}")
                cards_drawn = GameActions.draw_from_deck(deck, hand, 2)
                evolution_msgs.append(f"Sylveon ex drew {cards_drawn} cards")
                evolution_msgs.append(f"Hand after drawing:[{', '.join(c['name'] for c in hand)}]")
                evolved = True
            elif eevee_target and eevee_target.get('just_placed', False):
                location = "active" if eevee_target in active_pokemon else "bench"
                evolution_msgs.append(f"Attempted to evolve {eevee_target['name']} to Sylveon ex in {location} but failed (just placed this turn)")
        
        return evolved, evolution_msgs
    
    @staticmethod
    def _try_regular_evolutions(hand, pokemon_in_play, active_pokemon, bench, deck, evolved, evolution_msgs):
        """Handle regular evolution logic."""
        while True:
            found_evolution = False
            for i, card in enumerate(hand):
                # Skip Sylveon ex since it was handled
                if card['name'] == 'sylveon ex':
                    continue

                if ((CardHelpers.is_stage1(card) or CardHelpers.is_stage2(card)) and 
                    EvolutionHelper.can_evolve(card, pokemon_in_play)):
                    
                    evolve_from = card.get('evolve_from', '')
                    valid_names = ['eevee', 'eevee ex'] if evolve_from == 'eevee' else [evolve_from]
                    
                    for target in pokemon_in_play:
                        if target.get('name', '') in valid_names and not target.get('just_placed', False):
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
                            found_evolution = True
                            
                            # Shiinotic special evolution rule
                            if evo_card['name'] == 'shiinotic' and target['name'] == 'morelull':
                                EvolutionActions._handle_shiinotic_evolution(deck, hand, evolution_msgs)
                            
                            break
                        elif target.get('name', '') in valid_names and target.get('just_placed', False):
                            location = "active" if target in active_pokemon else "bench"
                            evolution_msgs.append(f"Attempted to evolve {target['name']} to {card['name']} in {location} but failed (just placed this turn)")
                    
                    if found_evolution:
                        break
            
            if not found_evolution:
                break
        
        return evolved, evolution_msgs
    
    @staticmethod
    def _handle_shiinotic_evolution(deck, hand, evolution_msgs):
        """Handle Shiinotic's special evolution ability."""
        for j, deck_card in enumerate(deck):
            if deck_card.get('category', '') == 'pokemon':
                if len(hand) < 10:
                    found_poke = deck.pop(j)
                    hand.append(found_poke)
                    evolution_msgs.append(f"Shiinotic ability: drew {found_poke['name']} from deck on evolution")
                else:
                    evolution_msgs.append("Shiinotic ability: hand full, could not draw Pokémon card on evolution")
                break
        random.shuffle(deck)
        evolution_msgs.append("Shuffled deck after Shiinotic evolution ability")


class SpecialActions:
    """Handles special actions like switching and end-turn draws."""
    
    @staticmethod
    def try_switch_legendary_beast(hand, active_pokemon, bench, turn):
        """Try to get a legendary beast into the active position."""
        if any(CardHelpers.is_legendary_beast_ex(p) for p in active_pokemon):
            return False, None
        
        beast_on_bench = next((p for p in bench if CardHelpers.is_legendary_beast_ex(p)), None)
        if beast_on_bench and turn >= 2:
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
    
    @staticmethod
    def legendary_beast_end_turn_draw(deck, active_pokemon):
        """Draw 1 card if legendary beast is active."""
        if active_pokemon and CardHelpers.is_legendary_beast_ex(active_pokemon[0]):
            if deck:
                return [deck.pop(0)]
        return []
    
    @staticmethod
    def handle_shiinotic_ongoing_ability(deck, hand, active_pokemon, bench, evolution_msgs):
        """Handle Shiinotic's ongoing ability to draw Pokemon cards."""
        shiinotics_in_play = [p for p in active_pokemon + bench if p.get('name', '') == 'shiinotic']
        
        for shiinotic in shiinotics_in_play:
            for j, deck_card in enumerate(deck):
                if deck_card.get('category', '') == 'pokemon':
                    if len(hand) < 10:
                        found_poke = deck.pop(j)
                        hand.append(found_poke)
                        evolution_msgs.append(f"Shiinotic ability: drew {found_poke['name']} from deck (ongoing ability)")
                    else:
                        evolution_msgs.append("Shiinotic ability: hand full, could not draw Pokémon card (ongoing ability)")
                    break
            random.shuffle(deck)
            evolution_msgs.append("Shuffled deck after Shiinotic ongoing ability")


class MainAttackerAnalyzer:
    """Analyzes and identifies main attackers in the deck."""
    
    @staticmethod
    def get_main_attackers_and_evolution_methods(full_deck, card_data):
        """Identifies all potential main attackers and their evolution methods."""
        main_attackers = set()
        evolution_methods = {}
        has_rare_candy = any(CardHelpers.is_rare_candy(c) for c in full_deck)
        
        # Group Pokémon by their basic ancestor
        evolution_lines = {}
        for card in full_deck:
            if card['category'] != 'pokemon':
                continue
            basic_name = (EvolutionHelper.get_evolves_from_chain(card.get('evolve_from', ''), card_data.all_card_data) 
                         if card.get('evolve_from', '') else card['name'])
            evolution_lines.setdefault(basic_name, []).append(card)

        # Add all Stage 2, Stage 1 EX, Basic EX
        for cards in evolution_lines.values():
            for card in cards:
                name = card['name']
                if CardHelpers.is_stage2(card):
                    evolution_methods[name] = 'Stage 2 (via Rare Candy)' if has_rare_candy else 'Stage 2'
                    main_attackers.add(name)
                elif CardHelpers.is_stage1(card) and card.get('ex', False):
                    evolution_methods[name] = 'Stage 1 ex'
                    main_attackers.add(name)
                elif CardHelpers.is_basic(card) and card.get('ex', False):
                    evolution_methods[name] = 'Basic ex'
                    main_attackers.add(name)

        # Add standalone basics not part of any evolution line
        evolved_from_names = set(c.get('evolve_from', '') for c in full_deck if c.get('evolve_from', ''))
        basics_with_stage2_rare_candy = MainAttackerAnalyzer._get_basics_with_stage2_rare_candy(
            full_deck, has_rare_candy, card_data
        )

        for card in full_deck:
            if CardHelpers.is_basic(card):
                basic_name = card['name']
                if (basic_name not in evolved_from_names and 
                    basic_name not in basics_with_stage2_rare_candy):
                    evolution_methods[basic_name] = 'Basic (standalone)'
                    main_attackers.add(basic_name)

        # Stage 1 evos that don't have any further evos
        for cards in evolution_lines.values():
            for card in cards:
                if (CardHelpers.is_stage1(card) and 
                    card["name"] not in card.get('evolve_from', [])):
                    evolution_methods[card['name']] = 'Stage 1 (standalone)'
                    main_attackers.add(card['name'])

        # Clean up special cases
        main_attackers.discard('eevee ex')
        
        # Remove basics that have evolutions in the deck
        for card in full_deck:
            if (CardHelpers.is_basic(card) and 
                card["name"] in card.get('evolve_from', [])):
                evolution_methods[card['name']] = 'Basic (with evolution)'
                main_attackers.discard(card['name'])

        return list(main_attackers), evolution_methods
    
    @staticmethod
    def _get_basics_with_stage2_rare_candy(full_deck, has_rare_candy, card_data):
        """Find all basics that have a stage2 in deck that ultimately evolves from them."""
        basics_with_stage2_rare_candy = set()
        
        if has_rare_candy:
            for basic_card in full_deck:
                if CardHelpers.is_basic(basic_card):
                    basic_name = basic_card['name']
                    for evo_card in full_deck:
                        if CardHelpers.is_stage2(evo_card):
                            ancestor = (EvolutionHelper.get_evolves_from_chain(
                                evo_card.get('evolve_from', ''), card_data.all_card_data
                            ) if evo_card.get('evolve_from', '') else evo_card['name'])
                            
                            if ancestor == basic_name:
                                basics_with_stage2_rare_candy.add(basic_name)
                                break
        
        return basics_with_stage2_rare_candy


class GameSimulator:
    """Main game simulator class."""
    
    def __init__(self, card_data: CardData):
        self.card_data = card_data
    
    def ensure_guaranteed_basic_top5(self, deck):
        """Ensures at least one basic Pokemon is in the top 5 cards."""
        opener = deck[:5]
        if any(CardHelpers.is_basic(c) for c in opener):
            return deck
        
        for i in range(5, len(deck)):
            if CardHelpers.is_basic(deck[i]):
                j = random.randrange(5)
                deck[i], deck[j] = deck[j], deck[i]
                return deck
        
        return deck
    
    def simulate_one_trial_with_logging(self, full_deck, precomputed_attackers, max_turns=6, log_details=False):
        """Simulate one game with detailed logging."""
        deck = full_deck[:]
        random.shuffle(deck)
        deck = self.ensure_guaranteed_basic_top5(deck)
        
        hand = deck[:5]
        deck = deck[5:]
        
        active_pokemon = []
        bench = []
        log = []
        
        if log_details:
            log.append("=== GAME START ===")
            log.append(f"Opening hand: {[c['name'] for c in hand]}")
        
        # Place initial basics
        placed = GameActions.place_basic_pokemon(hand, active_pokemon, bench)
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
                drawn = GameActions.draw_from_deck(deck, hand, 1)
                if log_details and drawn > 0:
                    drawn_card = hand[hand_size_before]
                    log.append(f"Drew card: {drawn_card['name']}")

                # Shiinotic ongoing ability
                if log_details:
                    evolution_msgs = []
                    SpecialActions.handle_shiinotic_ongoing_ability(
                        deck, hand, active_pokemon, bench, evolution_msgs
                    )
                    for msg in evolution_msgs:
                        log.append(msg)
                else:
                    SpecialActions.handle_shiinotic_ongoing_ability(
                        deck, hand, active_pokemon, bench, []
                    )
            
            # Main action loop
            while True:
                action_taken = False
                
                # Play supporter
                played_supporter, supporter_msg = GameActions.try_play_supporter(hand, deck, supporter_used)
                if played_supporter:
                    action_taken = True
                    if log_details:
                        log.append(f"Played supporter: {supporter_msg}")
                
                # Place any new basics
                placed = GameActions.place_basic_pokemon(hand, active_pokemon, bench)
                if placed:
                    action_taken = True
                    if log_details:
                        for location, name in placed:
                            log.append(f"Placed {name} in {location}")
                cards_seen.update(c['name'] for c in active_pokemon + bench)
                
                # Play Poke Balls
                played_pokeball, pokeball_msg = GameActions.try_play_pokeball(hand, deck)
                if played_pokeball:
                    action_taken = True
                    if log_details:
                        log.append(f"Played Poké Ball: {pokeball_msg}")
                    cards_seen.update(c['name'] for c in hand)
                
                # Try evolutions
                evolved, evolution_msg = EvolutionActions.try_evolve(
                    hand, active_pokemon, bench, deck, supporter_used, turn, self.card_data
                )
                if evolved:
                    action_taken = True
                    if log_details:
                        log.append(f"Evolution: {evolution_msg}")
                    cards_seen.update(c['name'] for c in active_pokemon + bench)
                
                # Try to switch legendary beast to active
                switched, switch_msg = SpecialActions.try_switch_legendary_beast(
                    hand, active_pokemon, bench, turn
                )
                if switched:
                    action_taken = True
                    if log_details:
                        log.append(f"Switch: {switch_msg}")

                if not action_taken:
                    break
            
            if (log_details and turn < 2 and 
                any(CardHelpers.is_stage1(c) or CardHelpers.is_stage2(c) for c in hand)):
                evos_in_hand = [c['name'] for c in hand 
                               if CardHelpers.is_stage1(c) or CardHelpers.is_stage2(c)]
                log.append(f"Evolution cards in hand (can't use until turn 2): {evos_in_hand}")
            
            # End of turn: Legendary beast draw
            beast_draw = SpecialActions.legendary_beast_end_turn_draw(deck, active_pokemon)
            if beast_draw:
                cards_drawn_at_end.extend(beast_draw)
                if log_details:
                    log.append(f"Legendary beast end-turn draw: {beast_draw[0]['name']} (available next turn)")

        # Determine bricking status
        is_brick, brick_no_attacker, brick_key_stuck = self._analyze_brick_status(
            full_deck, active_pokemon, bench, cards_seen, precomputed_attackers
        )
        
        if log_details:
            self._add_final_state_logs(log, active_pokemon, bench, hand, deck, 
                                     precomputed_attackers, full_deck, is_brick)
        
        return is_brick, brick_no_attacker, brick_key_stuck, log
    
    def _analyze_brick_status(self, full_deck, active_pokemon, bench, cards_seen, precomputed_attackers):
        """Analyze if the game state is bricked."""
        all_pokemon_in_play = active_pokemon + bench
        developed_attackers = [p for p in all_pokemon_in_play 
                              if CardHelpers.is_main_attacker(p, precomputed_attackers)]
        
        # Get total count of each main attacker in the deck
        attacker_names = set(c['name'] for c in full_deck 
                            if CardHelpers.is_main_attacker(c, precomputed_attackers))
        total_main_attackers_in_deck = len(attacker_names)

        # Check if a game state is NOT a brick
        required_in_play = 3 if total_main_attackers_in_deck > 3 else max(2, total_main_attackers_in_deck)
        is_not_brick = len(developed_attackers) >= required_in_play
        is_brick = not is_not_brick

        # Existing key card stuck and no attacker logic (for logging purposes only)
        key_cards = ['professor\'s research']
        key_basics = [c['name'] for c in full_deck 
                     if CardHelpers.is_basic(c) and CardHelpers.is_important(c)]
        deck_counts = Counter(card['name'] for card in full_deck 
                             if card['name'] in key_cards or card['name'] in key_basics)
        seen_counts = Counter(name for name in cards_seen if name in deck_counts)
        key_cards_stuck = [name for name, total in deck_counts.items() 
                          if seen_counts.get(name, 0) == 0]
        
        brick_no_attacker = len(developed_attackers) < required_in_play
        brick_key_stuck = len(key_cards_stuck) > 0
        
        return is_brick, brick_no_attacker, brick_key_stuck
    
    def _add_final_state_logs(self, log, active_pokemon, bench, hand, deck, 
                             precomputed_attackers, full_deck, is_brick):
        """Add final state information to the log."""
        developed_attackers = [p for p in active_pokemon + bench 
                              if CardHelpers.is_main_attacker(p, precomputed_attackers)]
        attacker_names = set(c['name'] for c in full_deck 
                            if CardHelpers.is_main_attacker(c, precomputed_attackers))
        total_main_attackers_in_deck = len(attacker_names)
        
        log.append(f"\n--- FINAL STATE ---")
        log.append(f"Active: {[c['name'] for c in active_pokemon]}")
        log.append(f"Bench: {[c['name'] for c in bench]}")
        log.append(f"Hand: {[c['name'] for c in hand]}")
        log.append(f"Main attackers in play: {[c['name'] for c in developed_attackers]}")
        log.append(f"Total main attackers in deck: {total_main_attackers_in_deck}")
        
        log.append(f"RESULT: {'BRICK' if is_brick else 'OK'}")
        
        if is_brick:
            log.append("  - Bricking condition met:")
            required_in_play = 3 if total_main_attackers_in_deck > 3 else max(2, total_main_attackers_in_deck)
            if total_main_attackers_in_deck > 3:
                log.append(f"    - Less than 3 attackers ({len(developed_attackers)}) developed when deck has >3 attackers.")
            else:
                log.append(f"    - Not all attackers ({len(developed_attackers)} of {total_main_attackers_in_deck}) developed.")
        
        log.append(f"Remaining deck: {[c['name'] for c in deck]}")
    
    def simulate_brick_rate_with_examples(self, full_deck, precomputed_attackers, 
                                         trials=1000, show_examples=5, maxturns=7):
        """Run multiple simulations and show detailed examples of bricked games."""
        total_bricks = 0
        attacker_bricks = 0
        key_card_bricks = 0
        example_logs = []

        for i in range(trials):
            is_brick, brick_attacker, brick_key, log = self.simulate_one_trial_with_logging(
                full_deck, precomputed_attackers, log_details=True, max_turns=maxturns
            )

            if is_brick:
                total_bricks += 1
                if brick_attacker:
                    attacker_bricks += 1
                if brick_key:
                    key_card_bricks += 1

                if len(example_logs) < show_examples:
                    example_logs.append(log)

        return total_bricks, attacker_bricks, key_card_bricks, trials, example_logs


class DeckAnalyzer:
    """Main class for analyzing Pokemon decks."""
    
    def __init__(self):
        self.card_data = CardData()
        self.deck_parser = DeckParser(self.card_data)
        self.simulator = GameSimulator(self.card_data)
    
    def analyze_deck(self, decklist_text, trials=1000, show_examples=5, max_turns=7):
        """Complete deck analysis workflow."""
        # Load card data
        if not self.card_data.load_from_csv():
            print("Failed to load card data.")
            return
        
        # Parse deck
        try:
            parsed_deck = self.deck_parser.parse_decklist(decklist_text)
        except ValueError as e:
            print(f"Failed to parse deck: {e}")
            return
        
        # Display deck information
        self._display_deck_info(parsed_deck)
        
        # Analyze main attackers
        main_attackers, evolution_methods = MainAttackerAnalyzer.get_main_attackers_and_evolution_methods(
            parsed_deck, self.card_data
        )
        self._display_main_attackers(main_attackers, evolution_methods)
        
        # Run simulation
        total_bricks, attacker_bricks, key_card_bricks, trials, example_logs = (
            self.simulator.simulate_brick_rate_with_examples(
                parsed_deck, main_attackers, trials, show_examples, max_turns
            )
        )
        
        # Display results
        self._display_simulation_results(
            total_bricks, attacker_bricks, key_card_bricks, trials, example_logs
        )
    
    def _display_deck_info(self, parsed_deck):
        """Display basic deck information."""
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
            print(f"   - {name}: category={card['category']}, stage={card['stage']}, ex={card['ex']}{evolve_info}")
    
    def _display_main_attackers(self, main_attackers, evolution_methods):
        """Display identified main attackers and their evolution methods."""
        print("\nPrecomputed main attackers and evolution methods:")
        for attacker in main_attackers:
            print(f"   - {attacker}: {evolution_methods.get(attacker, 'N/A')}")
    
    def _display_simulation_results(self, total_bricks, attacker_bricks, key_card_bricks, 
                                   trials, example_logs):
        """Display simulation results and examples."""
        if not example_logs:
            print("No bricked game examples to show.")
        
        for i, example in enumerate(example_logs, 1):
            print(f"\n--- BRICKED GAME EXAMPLE #{i} ---")
            for line in example:
                print(line)
                
        print(f"\n--- SIMULATION RESULTS ({trials} trials) ---")
        print(f"Total strict bricks (unplayable hands): {total_bricks} ({total_bricks/trials*100:.2f}%)")
        print(f"Sub-optimal games due to not enough main attackers in play: {attacker_bricks} ({attacker_bricks/trials*100:.2f}%)")
        
        if attacker_bricks > 0:
            key_card_percentage = key_card_bricks/attacker_bricks*100
            total_percentage = key_card_bricks/trials*100
            print(f"   - Of these, caused by key cards not drawn in time: {key_card_bricks} ({key_card_percentage:.2f}% of sub-optimal games) and ({total_percentage:.2f}% of all games)")
        
        print(f"Note: Some sub-optimal situations are temporary and may resolve in later turns.")


def main():
    """Main function to run the deck analysis."""
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
    
    analyzer = DeckAnalyzer()
    analyzer.analyze_deck(deck_text, trials=1000, show_examples=5, max_turns=7)


if __name__ == "__main__":
    main()