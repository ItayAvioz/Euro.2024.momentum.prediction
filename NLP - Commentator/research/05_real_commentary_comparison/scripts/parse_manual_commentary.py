"""
Parse manually extracted Sports Mole commentary into structured CSV
Includes classification for red (key events) vs black (general commentary) lines
"""

import pandas as pd
import re

# Manual commentary text
manual_text = """
1 min
KICKOFF:  England kick us off here...

2 min
... England immediately look down the right, with Pickford delivering long towards Saka, but it goes behind for a Spain goal kick. The atmosphere inside the stadium really is sensational.

3 min
Shaw wins his first battle against Yamal, knocking the Barcelona teenager to the ground in the process, but you can be sure that the 17-year-old will come back time and time again.

5 min
Spain are looking to control the possession early on here, which is not a surprise. England are dropping into their shape, though, and look relatively comfortable in there. Shaw again wins his battle against Yamal, which will give England plenty of confidence early here.

7 min
Pass, pass, pass from Spain, who have been the better outfit in the first seven minutes. England, though, are not overly concerned at this moment in time. Cagey start here.

9 min
England have not yet managed to break clear, but the opportunity will be there at some stage, as Spain are pushing really high. No doubt that La Roja have started the better here, with Williams looking dangerous down the left. Ruiz has also been impressive in midfield.

11 min
England deliver a deep free kick into the Spain box, but Guehi pushes Rodri to the ground, and Spain are able to gather control of the ball once again here.

13 min
CLOSE!  Some concern over Walker here, who stays down after a challenge, but he should be able to continue. Le Normand then hooks one behind from a corner, with Spain having a half-chance.

15 min
Trippier is warming up here amid the concerns over Walker, but it does appear that the Manchester City defender will be able to continue. Still all square in the final.

16 min
Walker breaks into a dangerous position for England, and his low cross is cleared behind by Laporte. Much better for England, who have their first corner of the match...

16 min
... Rodri does really well to clear the danger.

18 min
Rodri again does brilliantly to block a strike from Rice, before Cucurella clears at the far post. England are suddenly turning up the heat here, with Foden also involved.

19 min
Shaw again wins a personal battle with Yamal. He's been brilliant.

20 min
Much more of an even game at the moment, with England relatively comfortable in their shape, while Spain have been forced to make some clearances over the last few minutes. Shaw has been England's standout player thus far, while Rodri has been excellent for Spain.

22 min
Some thoughts from Senior Reporter Ben Knapton...

22 min
"Unlike the semi-final, this has been a much more tentative start from the Three Lions, who have conceded the lion's share of possession to Spain, albeit while defending resolutely - John Stones and Declan Rice have done their bits to snuff out attacks. While Nico Williams is looking lively on the left, Lamine Yamal is yet to get the better of Luke Shaw, making his first England start in over 12 months. Southgate's risky call is paying off so far, but this one is still waiting to explode into life."

24 min
Not too much happening at the moment. We are still waiting for the first major chance here. Spain are controlling the possession, but England will also be relatively comfortable.

25 min
Carvajal is on his last warning here after pulling Saka to the ground...

25 min
YELLOW CARD!  Kane picks up the first yellow of the match for a late tackle on Ruiz.

27 min
Mainoo is throwing his weight around in midfield at the moment, with the Manchester United youngster starting to make his mark, but he is up against two wonderful players in the shape of Rodri and Ruiz. It remains goalless in the Euro 2024 final with 27 minutes on the clock.
Ruiz will be able to continue here despite limping after that Kane tackle.

28 min
SAVE!  Ruiz strikes one towards goal, but it deflects off Guehi and into the arms of Pickford. Good work from Spain there, but again England manage to deal with the danger.

30 min
Little over 15 minutes of the first period remaining here. Bellingham has just attempted to gather a long pass down the left, but Carvajal is across to deal with the danger.

31 min
YELLOW CARD!  Olmo is in the book for Spain for a foul on Rice.

32 min
Rice is still down here, it was a nasty kick in his stomach from Olmo.

34 min
Stop-start game at the moment, with the referee being forced to intervene due to some late tackles. Little over 10 minutes until the end of the first period, and it has flown past.

36 min
Laporte wants a penalty, as Rice pulls him to the ground, but the referee is not interested and VAR agree. Spain have another corner, but England again deal with it, as Kane blocks Olmo's shot.

38 min
Spain are on the front foot at the moment, but we are still waiting for the first serious chance of the match. England just need to find a way to relieve some of the pressure.

40 min
We have not seen too much from Foden and Bellingham in this first period, with Spain dealing with the England duo, but the Three Lions are having some possession in the Spain half in the latter stages of the first period. Stones has just burst forward, but Spain clear.

42 min
Williams breaks clear down the left, but he has to cut back, and Spain look to go down the other side. Nothing to separate the two teams in the opening half of action.

43 min
Morata has just broken into the England box, but Stones and Guehi between them manage to make the clearance, as Spain have another corner here.

45 min
England have a free kick in a dangerous area, as Williams fouls Walker...

45 min+1
CHANCE!  ... best chance of the match! The ball comes to Foden at the far post following a deep free kick, but Simon is on hand to make a smart save. Foden got good contact on the ball!

45 min+2
We are into the second of two added minutes at the end of the first period.

45 min+3
HALF TIME:  SPAIN 0-0 ENGLAND

9.04pm
SPAIN SUB! Zubimendi is replacing Rodri, who is surely injured. What a huge blow for Spain here! England must take so much confidence from that change.

46 min
KICKOFF:  Spain restart the contest here.

47 min
No word of the issue for Rodri, but it simply has to be a fitness problem, as he is his country's most important player. It is a huge blow for La Roja, but Zubimendi is a super player.
A Real Sociedad midfielder who is admired by the likes of Arsenal and Barcelona.

47 min
GOAL!  SPAIN 1-0 ENGLAND (WILLIAMS)

47 min
Oh my goodness me - what a goal! Spain make the breakthrough early in the second period as Yamal sets up Williams, who places one into the bottom corner. Super finish!

48 min
England simply have not started in the second period.

49 min
CHANCE!  Huge chance for Spain to score a second, as Williams finds Olmo inside the England box, but he fires wide of the post. It really should have been 2-0 to La Roja there.

51 min
Bit of possession for England at the moment, but Spain are comfortable in their shape.

53 min
Southgate will not be thinking about changes this early, but it will be interesting to see how he views the match over the next five or 10 minutes if it stays 1-0. England need more.

53 min
YELLOW CARD!  Stones is booked for pulling Zubimendi to the ground.

55 min
Some thoughts from Senior Reporter Ben Knapton...

55 min
"How a few minutes can make all the difference in football! Optimism may have been rife among England fans when Rodri failed to emerge for the second half, but Spain's wing wizards live up to the hype. Yamal - now on four assists for the tournament - expertly let the ball run across his body before picking out the untracked run of Williams, who did what Williams does. Spain exploded out of the blocks at the start of the second half, and they have been rewarded."

56 min
CHANCE!  Big chance for Spain again, as Morata breaks into the box and looks to pick out the bottom corner, but Stones is across to make the clearance, almost off the line!

56 min
CLOSE!  Williams swings one just wide of the post. Spain are all over this final!

58 min
Southgate must be thinking about changes here. Something needs to happen.

60 min
Little over 30 minutes of the second period remaining here, and England are about to introduce Watkins. Surely it will be Kane to leave the field in the final?

61 min
ENGLAND SUB! Watkins indeed replaces Kane here.

63 min
Possession for England at the moment, but not too much is happening with it. Will Spain be made to regret not scoring a second? England have been here before in the tournament.

65 min
Here was the moment...

65 min
CLOSE!  Bellingham turns on the edge of the Spain box and then looks to pick out the bottom corner, but his effort is just wide of the post. Much better from England there!

66 min
Spain are not having it their own way at the moment. England have survived their wobble without conceding a second, and this final is very much still alive.

67 min
SAVE!  Brilliant save from Pickford to keep out a low strike from Yamal, who had broken past Shaw and then looked to pick out the bottom corner. Excellent goalkeeping from Pickford.

68 min
SPAIN SUB! Morata is replaced by Oyarzabal for Spain.

70 min
CLOSE!  Fabian Ruiz hits one just over the crossbar, as Spain threaten a second. Still plenty of time left in this final, and it is delicately poised. Another change is coming here...

70 min
... ENGLAND SUB! Palmer replaces Mainoo for England.

71 min
Smart defending from Laporte to clear ahead of Saka, as England cause problems with another long ball. Watkins is stretching Spain, and suddenly De la Fuente's side look uncomfortable.

72 min
SAVE!  Easy save for Pickford to keep out a low strike from Oyarzabal.

73 min
GOAL!  SPAIN 1-1 ENGLAND (PALMER)

73 min
All square in the final! Palmer smashes one past Simon from the edge of the box to level the scores! Saka was down the right, Bellingham then set up Palmer, and the Chelsea attacker managed to find the back of the net to level it up in Berlin.

75 min
Palmer has been sensational since he entered the field. What a footballer.

77 min
There is going to be a winner in normal time here, I can sense it.
Spain are being made to regret not scoring a second when they had the chance, and England have responded yet again. We are all square in the final approaching the final 10 minutes.

78 min
"Palmer always cuts a composed demeanour on the field, but the Chelsea man could not help but explode into elation after that stunning equaliser! Once again, Southgate's substitutions have a devastating impact, and the Chelsea man's finish from outside the box could not have been more exquisite. England came from behind to win their last-16, quarter-final and semi-final ties. They couldn't do it again, could they?"

79 min
Here is the leveller...

80 min
Spain have settled after conceding, and they are looking strong again here.

82 min
A goal now surely wins it. I still feel like there is another before the end of normal time. Spain are dominating the possession at the moment, with England sitting in their shape.

82 min
SAVE!  Another super save from Pickford to keep out a strike from Yamal, who had been found after smart work from Williams and Olmo. Another big moment from the goalkeeper.

83 min
SPAIN SUB! Nacho enters the field for Le Normand.

85 min
Spain are knocking on the door at the moment, but England hold firm.

86 min
Pickford again does well to gather a cross from Yamal, who continues to look dangerous down the right for Spain. We are heading towards the final stages of normal time here.

86 min
GOAL!  SPAIN 2-1 ENGLAND (OYARZABAL)

86 min
Goodness me. Spain score a second in the 86th minute, as Oyarzabal turns a low Cucurella cross into the back of the net. Hint of offside, but the flag stays down, and he's on.

87 min
Super goal that. No question. England do not have long left to turn this one.

89 min
ENGLAND SUB! Toney replaces Foden here.

89 min
SPAIN SUB! Merino enters the field for Yamal.

90 min
CHANCE!  Oh my word. How? How has it not gone in? England have a header from Guehi cleared off the line by Olmo, before Rice heads over. Simon also kept out an effort in there. Spain survive.

90 min+1
We are into the first of four additional minutes here.

90 min+2
YELLOW CARD!  Watkins picks up a yellow card for kicking Nacho in the stomach.

90 min+3
Spain are almost there. England are going to fall just short here, unless...

90 min+3
... still time for England, who have a free kick inside their own half.

90 min+4
Saka has just fouled Cucurella, and Spain are almost there.

90 min+5
FULL TIME:  SPAIN 2-1 ENGLAND
"""


def parse_minute(minute_str):
    """Extract minute number and +time from string like '45 min+1'"""
    match = re.match(r'(\d+)\s*min(?:\+(\d+))?', minute_str.strip())
    if match:
        base_minute = int(match.group(1))
        plus_time = int(match.group(2)) if match.group(2) else 0
        return base_minute, plus_time
    # Handle time format like "9.04pm"
    if 'pm' in minute_str or 'am' in minute_str:
        return None, None
    return None, None


def classify_line_type(text):
    """
    Classify line as RED (key event) or BLACK (general commentary)
    Based on the images provided
    """
    # Key event markers (RED lines)
    red_markers = [
        'KICKOFF:', 'GOAL!', 'SAVE!', 'YELLOW CARD!', 'RED CARD!',
        'CHANCE!', 'CLOSE!', 'HALF TIME:', 'FULL TIME:',
        'SUB!', 'PENALTY!'
    ]
    
    text_upper = text.upper()
    for marker in red_markers:
        if marker in text_upper:
            return 'key_event'
    
    return 'general'


def infer_event_type(text):
    """Infer specific event type from commentary text"""
    text_lower = text.lower()
    text_upper = text.upper()
    
    if 'KICKOFF:' in text:
        return 'Kick Off'
    elif 'GOAL!' in text:
        return 'Goal'
    elif 'YELLOW CARD!' in text:
        return 'Yellow Card'
    elif 'RED CARD!' in text:
        return 'Red Card'
    elif 'SAVE!' in text:
        return 'Save'
    elif 'CHANCE!' in text:
        return 'Chance'
    elif 'CLOSE!' in text:
        return 'Close Call'
    elif 'HALF TIME:' in text:
        return 'Half Time'
    elif 'FULL TIME:' in text:
        return 'Full Time'
    elif 'SUB!' in text:
        return 'Substitution'
    elif 'corner' in text_lower:
        return 'Corner'
    elif 'cross' in text_lower and ('swings' in text_lower or 'delivers' in text_lower):
        return 'Cross'
    elif 'free kick' in text_lower:
        return 'Free Kick'
    elif 'penalty' in text_lower:
        return 'Penalty'
    elif 'thoughts from' in text_lower:
        return 'Analysis'
    else:
        return 'General'


def extract_players(text):
    """Extract player names mentioned"""
    # Common player names from the final
    players = [
        'Pickford', 'Walker', 'Stones', 'Guehi', 'Shaw', 'Trippier',
        'Rice', 'Bellingham', 'Foden', 'Saka', 'Kane', 'Mainoo', 
        'Palmer', 'Watkins', 'Toney',
        'Simon', 'Carvajal', 'Laporte', 'Le Normand', 'Cucurella', 'Nacho',
        'Rodri', 'Ruiz', 'Olmo', 'Zubimendi', 'Merino',
        'Yamal', 'Williams', 'Morata', 'Oyarzabal'
    ]
    
    mentioned = []
    for player in players:
        if player in text:
            mentioned.append(player)
    
    return ', '.join(mentioned) if mentioned else ''


def determine_team_focus(text):
    """Determine which team the commentary focuses on"""
    spain_count = text.lower().count('spain')
    england_count = text.lower().count('england')
    
    if spain_count > england_count:
        return 'Spain'
    elif england_count > spain_count:
        return 'England'
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
        
        # Check if this is a minute marker
        base_min, plus_time = parse_minute(line)
        
        if base_min is not None:
            # This is a minute marker
            current_minute = base_min
            current_plus = plus_time
            
            # Get the next line (commentary text)
            i += 1
            if i < len(lines):
                commentary_text = lines[i].strip()
                
                if commentary_text:
                    # Create entry
                    entry = {
                        'match_id': 'final',
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
    print("PARSING MANUALLY EXTRACTED SPORTS MOLE COMMENTARY")
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
        print(f"  • {event:.<20} {count:>3}")
    
    # Save to CSV
    output_file = '../data/sports_mole_final_commentary_COMPLETE.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    
    print(f"\n✅ SUCCESS! Saved to: {output_file}")
    print(f"   Total entries: {len(df)}")
    print(f"   Columns: {', '.join(df.columns)}")
    
    # Show sample of key events
    print(f"\n{'='*70}")
    print("SAMPLE KEY EVENTS (RED LINES):")
    print('='*70)
    
    key_events = df[df['line_type'] == 'key_event'].head(10)
    for _, row in key_events.iterrows():
        text = row['commentary_text'][:100] + '...' if len(row['commentary_text']) > 100 else row['commentary_text']
        print(f"\n🔴 {row['minute_display']:>6} min [{row['event_type']}]: {text}")


if __name__ == "__main__":
    main()

