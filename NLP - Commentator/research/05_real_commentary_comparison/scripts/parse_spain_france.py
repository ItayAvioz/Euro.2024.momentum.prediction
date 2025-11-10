"""
Parse Spain vs France Semi-Final commentary
Converts time format (8.00pm, 9.02pm) to match minutes
"""

import pandas as pd
import re

# Manual commentary text
manual_text = """
8.00pm
KICKOFF:  And we're off! France get us started.
Hopefully a memorable contest will be in store!

8.02pm
Bright start from Spain... Fabian Ruiz moves into the left channel and curls a cross towards the back post, but Lamine Yamal slips and the ball bounces out of play.

8.04pm
CHANCE!  Yamal and Ruiz are involved again for Spain, with the former this time setting up the latter from right to left. However, Ruiz can only head his effort at the far post over the crossbar.

8.04pm
CHANCE!  Yamal and Ruiz are involved again for Spain, with the former this time setting up the latter from right to left. However, Ruiz can only head his effort at the far post over the crossbar.

8.06pm
Kylian Mbappe - without his mask tonight after breaking his nose at the start of the tournament - had the ball poked away from his feet on the edge of the penalty area by Jesus Navas.

8.09pm
GOAL!  SPAIN 0-1 FRANCE (KOLO MUANI)

8.11pm
GOAL!  France finally score their first goal of Euro 2024 from open play!
Mbappe picks the ball up on the left flank and clips an inviting delivery towards the far post where Randal Kolo Muani is to nod the ball home, towering above Aymeric Laporte to head France into an early lead.

8.13pm
Spain have responded well to going a goal behind as they pile bodies forward and look threatening on both wings with Yamal and Nico Williams.

8.15pm
YELLOW CARD!  Navas is booked for a late sliding challenge on Rabiot around 35 yards away from Spain's goal... resulting free kick for France comes to nothing, though.

8.18pm
France are beginning to find their rhythm... this is the best they have played at Euro 2024, although they have yet to test the gloves of Unai Simon.

8.21pm
GOAL!  SPAIN 1-1 FRANCE (YAMAL)

8.23pm
GOAL!  Wow... that was special!
Spain restore parity in sensational fashion, with wonderkid Yamal whipping a delightful left-footed strike from the outside of the penalty area into the top corner, beating Mike Maignan all ends up.

8.25pm
GOAL!  SPAIN 2-1 FRANCE (OLMO)

8.27pm
GOAL!  

Within the blink of an eye, Spain have turned this thrilling contest around!

Dani Olmo drives into France's penalty box and knocks the ball past Aurelien Tchouameni before smacking a right-footed shot towards the bottom corner.

The Spaniard's strik beats Maignan before a lunging Jules Kounde helps the ball over the line.

8.31pm
UEFA state, at the moment, that Spain's second goal is in fact an own goal scored by France defender Jules Kounde, but that will surely change as Olmo's strike looked on target.
If it is Olmo's goal, he's now the joint top scorer at Euro 2024 with three goals.

8.35pm
Theo Hernandez leaves his mark on Yamal with a late challenge right on the touchline. Referee Slavko Vincic gives the foul but opts to keeps his cards in his pocket for this one

8.37pm
Thirty-seven brilliant minutes played in Munich so far; France have impressed despite letting a one-goal lead slip, but Spain's two goals scored just four minutes and nine seconds apart is what is separating the two teams at present.

8.39pm
CHANCE!  France win a corner and play it short; Theo Hernandez's cross is initially kept in by William Saliba, but it fails to reach a teammate.
Spain then burst forward on the counter-attack, and after being picked out by Williams, Yamal's shot is deflected behind for a corner by Hernandez.

8.41pm
Maignan leaps well to catch the resulting corner from Williams; the France goalkeeper then tries to get his team up the pitch with an early throw, but the options were not there in front of him for a quick breakaway.

8.44pm
As expected, UEFA have now awarded the second Spain goal to Dani Olmo, meaning the RB Leipzig attacker is officially joint top scorer at Euro 2024 with three goals.

8.45pm
Two minutes of added time.

9.02pm
KICKOFF:  Spain get us underway for the second half!
Hopefully more of the same!

9.04pm
CHANCE!  Maignan does well to come off his line and rush out of his box to win the ball from Williams on Spain's left flank.
Williams initially did well to cover the ground and make the challenge, but was ultimately unable to get their ahead of Maignan.

9.07pm
Ousmane Dembele does brilliantly to control a cross and stands up Spain left-back Marc Cucurella, but the PSG winger could only curl his delivery from the right into the gloves of Unai Simon... frustrating from France's perspective.

9.08pm
CHANCE!  Mbappe cuts inside from the left and fizzes a low shot towards the near post, but Unai Simon comfortably gets behind it.

9.09pm
Spain are forced to make their first substitution of the night, as right-back Navas seems to have picked up a knock and is replaced by Athletic Bilbao centre-back Dani Vivian, meaning Nacho is set to move over to the right side of the back four.

9.12pm
CHANCE!  Mbappe races down the right, easily beating Rodri for pace, before smacking a cross into the six-yard box, but Simon blocks the cross with a strong left hand.
France have shown a greater threat down the flanks in the second half.

9.17pm
YELLOW CARD!  Tchouameni is booked for a late lunging tackle on Morata in the middle of the pitch, preventing a Spanish counter-attack.

9.18pm
With half an hour remaining, Deschamps has opted to roll the dice...
A triple change sees Eduardo Camavinga, Antoine Griezmann and Bradley Barcola all brought on for Tchouameni, Rabiot and Kolo Muani

9.20pm
Antoine Griezmann (36) has now become France's most-capped player at major tournaments, surpassing goalkeeper Hugo Lloris (35).
Only three outfield players - Cristiano Ronaldo (52), Bastian Schweinsteiger (38) and Miroslav Klose (37) - have made more appearances at the Euros and World Cup combined than Griezmann.

9.22pm
France win another corner, but Dayot Upamecano heads wide at the back post... a lot of France's best chances have come through headers and this is another one that goes begging.

9.22pm
France win another corner, but Dayot Upamecano heads wide at the back post... a lot of France's best chances have come through headers and this is another one that goes begging.

9.25pm
Spain are yet to register a single shot on goal in the second half, while France have had three chances.

9.27pm
Spain have lost the spark they had in the first 45 and seem to be holding on here, as France enjoy an extended spell of possession and pose a threat in the final third.
It's all about game management for La Roja at the moment.

9.30pm
CHANCE!  Spain fail to clear their lines and a deflected cross from Dembele falls nicely to Theo Hernandez, in space on the edge of the box, but the French left-back blazes a right-foot shot over the crossbar.

9.32pm
Spain decide to make two changes ahead of the final 10 minutes of normal time, with Olmo and Morata brought off as Mikel Merino and Mikel Oyarzabal enter the pitch.
Rodri now wearing the captain's armband for La Roja.

9.36pm
Another change for France as their all-time record goalscorer Olivier Giroud is brought on for Dembele.
Can the 37-year-old striker net a late leveller for Les Bleus?

9.38pm
CHANCE!  Yamal, like the rest of his Spain teammates, has rarely threatened in the second half, but he almost put the game to bed with another speculative strike.
After cutting inside from the right on his favoured left foot, the teenager's unleashed a shot that flew just over the crossbar; it had plenty of power and curl, but not quite enough dip to fly into the top corner.

9.40pm
France's front three have scored a combined 149 goals at international level - Olivier Giroud (57), Kylian Mbappe (48) and Antoine Griezmann (44) - but they are still searching for that all-important equaliser.
Spain holding on here and managing the game well.

9.42pm
Spain defender Aymeric Laporte is down and receiving treatment after running into the shoulder of Giroud.
A nasty knock to the face for Laporte, whose face is covered in blood... ouch!

9.44pm
CHANCE!  Just moments after Laporte was cleared to continue, Mbappe was presented with a brilliant chance to restore parity fro France.
Real Madrid's summer signing is played through down the left by Barcola, and his eyes must have lit up as he cut inside and set himself for the shot.

However, Mbappe uncharacteristically fired his effort from 20 yards well over the crossbar, failing to test Simon between the sticks.

9.46pm
YELLOW CARD!  France are clearly getting frustrated now and Camavinga is deservedly booked for a late tackle on Marc Cucurella.

9.47pm
Five minutes of added time... can Spain hold on or can France find a late equaliser?

9.48pm
YELLOW CARD!  Yamal takes one for the team and receives a yellow card for pulling back Hernandez to prevent a French counter-attack.

9.50pm
Spain are looking to kill the pace of the game now... Merino picks out Williams on the left and the winger looks to keep the ball in the corner.

9.51pm
Spain make a late double substitution, with Yamal and Williams receiving a standing ovation from the jubilant Spanish supporters as they make way for Ferran Torres and Martin Zubimendi.
Time is running out for France...

9.52pm
A cross goes in to Spain's penalty box towards Griezmann, who heads it onto the roof of the net; the Frenchman is asking for a corner, but he does not get one.
That may well have been France's final chance.
"""


def convert_time_to_minute(time_str):
    """
    Convert time format (8.00pm, 9.02pm) to match minute
    8.00pm = minute 1 (kickoff first half)
    9.02pm = minute 46 (kickoff second half)
    """
    match = re.match(r'(\d+)\.(\d+)pm', time_str.strip())
    if match:
        hour = int(match.group(1))
        minute_part = int(match.group(2))
        
        if hour == 8:
            # First half: 8.00pm = minute 1
            # 8.02pm = minute 2, 8.09pm = minute 9, etc.
            if minute_part == 0:
                return 1, 0  # Kickoff
            else:
                return minute_part, 0
        
        elif hour == 9:
            # Second half: 9.02pm = minute 46
            # 9.04pm = minute 48, 9.07pm = minute 51, etc.
            if minute_part == 2:
                return 46, 0  # Second half kickoff
            else:
                # Calculate minutes elapsed in second half
                elapsed = minute_part - 2
                return 46 + elapsed, 0
    
    return None, None


def classify_line_type(text):
    """Classify line as RED (key event) or BLACK (general commentary)"""
    red_markers = [
        'KICKOFF:', 'GOAL!', 'SAVE!', 'YELLOW CARD!', 'RED CARD!',
        'CHANCE!', 'CLOSE!', 'SHOT!', 'OFF THE BAR!', 'PENALTY!',
        'SUB', 'HALF TIME:', 'FULL TIME:'
    ]
    
    text_upper = text.upper()
    for marker in red_markers:
        if marker in text_upper:
            return 'key_event'
    
    return 'general'


def infer_event_type(text):
    """Infer specific event type from commentary text"""
    text_upper = text.upper()
    
    if 'KICKOFF:' in text:
        return 'Kick Off'
    elif 'GOAL!' in text:
        return 'Goal'
    elif 'YELLOW CARD!' in text:
        return 'Yellow Card'
    elif 'SAVE!' in text:
        return 'Save'
    elif 'CHANCE!' in text:
        return 'Chance'
    elif 'CLOSE!' in text:
        return 'Close Call'
    elif 'SHOT!' in text:
        return 'Shot'
    elif 'OFF THE BAR!' in text:
        return 'Hit Bar'
    elif 'SUB' in text_upper:
        return 'Substitution'
    elif 'corner' in text.lower():
        return 'Corner'
    elif 'free kick' in text.lower():
        return 'Free Kick'
    else:
        return 'General'


def extract_players(text):
    """Extract player names mentioned"""
    # Spain players
    spain_players = [
        'Simon', 'Navas', 'Vivian', 'Laporte', 'Nacho', 'Cucurella',
        'Rodri', 'Ruiz', 'Olmo', 'Yamal', 'Williams', 'Morata',
        'Merino', 'Oyarzabal', 'Torres', 'Zubimendi'
    ]
    
    # France players
    france_players = [
        'Maignan', 'Kounde', 'Saliba', 'Upamecano', 'Hernandez',
        'Tchouameni', 'Rabiot', 'Camavinga', 'Griezmann',
        'Mbappe', 'Dembele', 'Kolo Muani', 'Barcola', 'Giroud'
    ]
    
    mentioned = []
    for player in spain_players + france_players:
        if player in text:
            mentioned.append(player)
    
    return ', '.join(mentioned) if mentioned else ''


def determine_team_focus(text):
    """Determine which team the commentary focuses on"""
    spain_keywords = ['spain', 'spanish', 'la roja']
    france_keywords = ['france', 'french', 'les bleus']
    
    text_lower = text.lower()
    
    spain_count = sum(text_lower.count(kw) for kw in spain_keywords)
    france_count = sum(text_lower.count(kw) for kw in france_keywords)
    
    if spain_count > france_count:
        return 'Spain'
    elif france_count > spain_count:
        return 'France'
    else:
        return 'Both'


def parse_commentary():
    """Parse the manual commentary into structured data"""
    
    lines = manual_text.strip().split('\n')
    entries = []
    current_minute = None
    current_plus = 0
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # Check if this is a time marker
        minute, plus_time = convert_time_to_minute(line)
        
        if minute is not None:
            current_minute = minute
            current_plus = plus_time
            
            i += 1
            if i < len(lines):
                commentary_text = lines[i].strip()
                
                if commentary_text:
                    entry = {
                        'match_id': 'spain_france',
                        'minute': current_minute,
                        'plus_time': current_plus,
                        'minute_display': f"{current_minute}+{current_plus}" if current_plus > 0 else str(current_minute),
                        'commentary_text': commentary_text,
                        'line_type': classify_line_type(commentary_text),
                        'event_type': infer_event_type(commentary_text),
                        'players_mentioned': extract_players(commentary_text),
                        'team_focus': determine_team_focus(commentary_text),
                        'commentary_length': len(commentary_text)
                    }
                    entries.append(entry)
        
        i += 1
    
    return pd.DataFrame(entries)


def main():
    print("\n" + "="*70)
    print("PARSING SPAIN VS FRANCE SEMI-FINAL")
    print("="*70)
    
    df = parse_commentary()
    
    print(f"\n✓ Parsed {len(df)} commentary entries")
    print(f"✓ Minute range: {df['minute'].min()} - {df['minute'].max()}")
    
    print(f"\nLine Type Distribution:")
    for line_type, count in df['line_type'].value_counts().items():
        emoji = "🔴" if line_type == "key_event" else "⚫"
        print(f"  {emoji} {line_type:.<15} {count:>3}")
    
    print(f"\nEvent Type Distribution:")
    for event, count in df['event_type'].value_counts().head(10).items():
        print(f"  • {event:.<20} {count:>2}")
    
    # Save to CSV
    output_file = '../data/sports_mole_spain_france_commentary.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\n✅ SUCCESS! Saved to: {output_file}")
    print(f"   Total entries: {len(df)}")
    
    # Show key events
    print(f"\n{'='*70}")
    print("KEY EVENTS TIMELINE:")
    print('='*70)
    
    key_events = df[df['line_type'] == 'key_event']
    for _, row in key_events.iterrows():
        text = row['commentary_text'][:60] + '...' if len(row['commentary_text']) > 60 else row['commentary_text']
        print(f"🔴 {row['minute_display']:>6} [{row['event_type']:<18}] {text}")


if __name__ == "__main__":
    main()

