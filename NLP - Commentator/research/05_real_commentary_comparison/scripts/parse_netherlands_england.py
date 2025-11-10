"""
Parse Netherlands vs England Semi-Final commentary
"""

import pandas as pd
import re

# Manual commentary text
manual_text = """
1 min
KICKOFF:  THE SECOND EURO 2024 SEMI-FINAL IS UNDERWAY!
England get us going in Dortmund.

2 min
Malen immediately tries a run in behind but the Dutchman is caught offside.
Early warning sign though.

4 min
England settle into a nice period of possession and Phil Foden wins a free kick off of Jerdy Schouten.
The Manchester City man already making his presence felt in the centre.

4 min
CHANCE!  The effervescent Simons charges forward on the right and tries to thread a pass into Malen, but Guehi does enough to shield the ball back to Jordan Pickford.

5 min
CHANCE!  England quickly go down the other end and Saka floats in a cross to the back stick, but Stefan de Vrij is there to clear.
End-to-end very early on.

7 min
Kieran Trippier goes for the long ball over the top to Bellingham - back in Dortmund territory - but it rolls harmlessly through to Bart Verbruggen.

7 min
GOAL!  NETHERLANDS 1-0 ENGLAND (SIMONS)

7 min
GOAL!  AND THAT IS WHAT XAVI SIMONS DOES. THE NETHERLANDS LEAD IN THE SEVENTH MINUTE.
Declan Rice is the guilty party, losing the ball to Simons in a dangerous area, and the Paris Saint-Germain starlet fires in a terrific 20-yard drive into the top corner!

10 min
Who would have had Simons out-muscling Rice down before the game? Certainly not me, but that was terrific work from the Dutchman.
England now have a free kick in a promising area as Bellingham is fouled...

12 min
Foden takes it but his Manchester City teammate Ake heads clear.
But Saka wins another almost immediately... albeit a bit further out. Positive response.

13 min
Trippier takes this one and finds Rice at the back post. The Arsenal man tries to cut back for a teammate but can only find the boot of Van Dijk.

14 min
SAVE!  HARRY KANE HAS A SHOT!
The Bayern Munich man tests Verbruggen from range, but the Brighton & Hove Albion man saves well down to his right.

14 min
SHOT!  Kane now fires over the top after a quick break and brilliant work from Saka!
But England want a penalty - their captain is down after a clash with Denzel Dumfries...

16 min
ZWAYER IS GOING TO THE SCREEN!

17 min
PENALTY!  PENALTY FOR ENGLAND!
Dumfries led in with his studs and caught the top of Kane's boot, and the Three Lions have the chance to respond almost immediately!

Kane to take as Dumfries is booked.

18 min
GOAL!  NETHERLANDS 1-1 ENGLAND (KANE)

18 min
GOAL!  Kane makes no mistake! Verbruggen dives the right way, but Kane's penalty is just too perfect.
England are back on terms, and they deserve it!

20 min
There will certainly be some debate about the awarding of the penalty - I initially didn't think it was, but upon seeing a replay, Dumfries did go in with his studs.
England's brilliant response is rewarded.

23 min
CLOSE!  WHAT. A. CLEARANCE!!!!

24 min
CLOSE!  Mainoo and Foden link up brilliantly as the latter prods the ball towards goal from a tight angle, and his toe-poke beats Verbruggen but Dumfries is there to stop the ball right on the line!

26 min
At the risk of jinxing it, this is by far England's best performance at Euro 2024 so far. The Dutch living incredibly dangerously and just unable to contain Southgate's inspired team.

29 min
SHOT!  The Netherlands go on one of their quick breaks, but a combination of Walker and Guehi denies Malen as the Netherlands win their first corner of the game.

30 min
OFF THE BAR!  Dumfries is absolutely everywhere tonight!
A Cristiano Ronaldo-esque leap from the right-back and his header clips the top of the bar. Pickford likely had it covered, though.

32 min
OFF THE BAR!  OH MY GOODNESS!
Foden is invited to shoot on his left foot from 25 yards - a nearly fatal mistake as his curler smacks the upright and goes behind!

33 min
Two woodwork hits in two minutes, a Kane penalty and a Simons stunner - this has been an utterly breathless start in Dortmund.

34 min
A chance for a breather now, though, as Memphis Depay is down and needs treatment.

35 min
NETHERLANDS SUB
Depay cannot continue and Koeman sends on PSV midfielder Joey Veerman, signalling a slight change in shape from the Dutchman, whose side have been overrun in midfield thus far.

37 min
Bellingham goes down under pressure from Schouten but Zwayer is not interested.

39 min
The Netherlands' shape already looks more rigid since the introduction of Veerman. England now reverting to a bit of slow build-up in front of an orange wall.

39 min
SHOT!  Just as I say that, Foden again tries to pick out the far corner from 25 yards, but Verbruggen - at full stretch - makes the save and holds onto the ball.

41 min
SHOT!  Mainoo - who has been exceptional so far - robs Gakpo and lets fly from range, but his strike smacks Nathan Ake and goes out for a throw.

43 min
Approaching half time, England can pat themselves on the back and then some. Whatever they had for breakfast at their hotel this morning has gone down a treat.

45 min
Southgate's men also ending the first 45 the better as Trippier gets down the left, but his cross is straight into Verbruggen's hands.

45 min
Three minutes added on.

45+2 min
Koeman's men keeping the ball well as the clock winds down, but England are holding their shape well.

Shaw IS coming on at half time and replaces Trippier. Meanwhile, Malen is off for the Netherlands, and the big man Weghorst is on.

46 min
KICKOFF:  The Netherlands get us back underway.

47 min
Let him know you're there and all that.
Weghorst clatters John Stones over within 43 seconds.

49 min
England quickly take control of the ball and Saka gets in behind Ake, but there is nobody there to receive his cutback.

51 min
The offside flag is up against England, but it's been another bright start from the men in white.

53 min
Patience is the name of the game right now for England, as Koeman's side have well and truly tightened up defensively.
Southgate's men just probing at the moment; Shaw's cross is blocked by Dumfries.

55 min
Mainoo has been an absolute force defensively and stands up to Simons on the right, before Tijjani Reijnders sends the ball straight out of play when looking for Dumfries.

57 min
I suspected the chances might dry up a bit when Koeman beefed up his midfield with the introduction of Veerman, and it has panned out exactly that way.
We're into one-moment-of-magic territory it seems. Not a lot to write home about at the start of the second half.

59 min
England still dominating possession but finding it far more difficult to penetrate the Orange wall.
Southgate's men are now attacking in the direction of the Dutch fans, by the way.

61 min
Koeman's men break quickly - surprise surprise - and Veerman tries to find Weghorst at the back post, but he overcooks his outswinging cross.

63 min
This now feels too reminiscent of England's first four matches at the tournament, struggling to find gaps in a compact backline, but the Dutch are not giving Pickford anything to think about either.

65 min
SAVE!  Veerman swings in a free kick for the Netherlands after Simons draws a foul by the dugouts, and Van Dijk gets his toe to it, forcing Pickford into a good reaction save!

66 min
SHOT!  From the resulting corner, Dumfries wins the header again, but he cannot keep this effort down.

68 min
Things are starting to happen for the Netherlands now, as Gakpo delivers a dangerous ball from the left, which Pickford has to punch behind for a corner.

69 min
Ake wins the header but Zwayer had spotted something that he didn't like. England free kick.

71 min
Time to mutter the dreaded two words, extra time?
At this point, it is difficult to see where a goal might come from.

72 min
YELLOW CARD!  Bellingham and De Vrij go in for a 50-50, but it is the England man who is penalised. Yellow card from Zwayer.

74 min
Saka down on the right after taking Ake's hand in his face, but no interest from the referee.

76 min
Surely both managers will be starting to think about changes pretty soon. Just the one alteration from Southgate, two from Koeman - one enforced.

78 min
SAVE!  Simons connects with a volley, but his connection is anything but clean - one bounce into the ground and Pickford gathers.

79 min
Cole Palmer and Ollie Watkins about to emerge for England.

79 min
DISALLOWED GOAL!  SAKA HAS THE BALL IN THE BACK OF THE NET, BUT THE OFFSIDE FLAG IS UP!

80 min
DISALLOWED GOAL!  Foden slips in Walker down the right, and the Manchester City man cuts back for Saka to guide home a brilliant first-time finish, but the right-back had just gone a bit too early.

81 min
ENGLAND SUBS
That was Foden's last contribution - he comes off for Palmer, while Watkins replaces... Kane. Big call.

84 min
Some beautiful play from Reijnders down the left, but Guehi stands up tall and takes the full force of Weghorst's 6ft 6in frame to snuff out the attack.

86 min
YELLOW CARD!  Gakpo is pushed over by Saka and the Netherlands have a free kick in a decent area...
Saka is booked to boot.

87 min
YELLOW CARD!  Stones gets a head to Veerman's free kick, but Zwayer gives a goal kick.
A furious Van Dijk is booked for his protests.

88 min
SHOT!  Saka sprays a sublime cross-field pass to Shaw, whose ball across is missed by Watkins, but Palmer picks it up and curls a strike over the top.

90 min
GOAL!  NETHERLANDS 1-2 ENGLAND (WATKINS)

90+1 min
GOAL!  OLLIE WATKINS MAY HAVE JUST SENT ENGLAND INTO THE EURO 2024 FINAL!
It's an absolutely brilliant finish from the Aston Villa man, who takes Palmer's pass to feet and finds the far side of the net from an incredibly tight angle!

Simons was booked for complaining about something in the aftermath.

90+2 min
NETHERLANDS SUBS
Two minutes were added on originally, but it will certainly be more now.

Simons and Dumfries off for Joshua Zirkzee and Brian Brobbey.

90+4 min
ENGLAND SUBS
At the same time, Saka and Mainoo have come off, Ezri Konsa and Conor Gallagher are on.
"""


def parse_minute(minute_str):
    """Extract minute number and +time from string"""
    match = re.match(r'(\d+)\s*min(?:\+(\d+))?', minute_str.strip())
    if match:
        base_minute = int(match.group(1))
        plus_time = int(match.group(2)) if match.group(2) else 0
        return base_minute, plus_time
    return None, None


def classify_line_type(text):
    """Classify line as RED (key event) or BLACK (general commentary)"""
    red_markers = [
        'KICKOFF:', 'GOAL!', 'SAVE!', 'YELLOW CARD!', 'RED CARD!',
        'CHANCE!', 'CLOSE!', 'SHOT!', 'OFF THE BAR!', 'PENALTY!',
        'DISALLOWED GOAL!', 'SUB', 'HALF TIME:', 'FULL TIME:'
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
    elif 'GOAL!' in text and 'DISALLOWED' not in text:
        return 'Goal'
    elif 'DISALLOWED GOAL!' in text:
        return 'Disallowed Goal'
    elif 'PENALTY!' in text:
        return 'Penalty'
    elif 'YELLOW CARD!' in text:
        return 'Yellow Card'
    elif 'SAVE!' in text:
        return 'Save'
    elif 'CHANCE!' in text:
        return 'Chance'
    elif 'CLOSE!' in text:
        return 'Close Call'
    elif 'OFF THE BAR!' in text:
        return 'Hit Bar'
    elif 'SHOT!' in text:
        return 'Shot'
    elif 'SUB' in text_upper:
        return 'Substitution'
    elif 'free kick' in text.lower():
        return 'Free Kick'
    elif 'corner' in text.lower():
        return 'Corner'
    else:
        return 'General'


def extract_players(text):
    """Extract player names mentioned"""
    # Netherlands players
    nl_players = [
        'Verbruggen', 'Dumfries', 'Van Dijk', 'De Vrij', 'Ake',
        'Schouten', 'Reijnders', 'Simons', 'Gakpo', 'Depay', 'Malen',
        'Veerman', 'Weghorst', 'Zirkzee', 'Brobbey'
    ]
    
    # England players
    eng_players = [
        'Pickford', 'Walker', 'Stones', 'Guehi', 'Trippier', 'Shaw',
        'Rice', 'Mainoo', 'Bellingham', 'Foden', 'Saka', 'Kane',
        'Palmer', 'Watkins', 'Konsa', 'Gallagher'
    ]
    
    mentioned = []
    for player in nl_players + eng_players:
        if player in text:
            mentioned.append(player)
    
    return ', '.join(mentioned) if mentioned else ''


def determine_team_focus(text):
    """Determine which team the commentary focuses on"""
    netherlands_keywords = ['netherlands', 'dutch', 'holland', 'oranje', 'orange']
    england_keywords = ['england', 'three lions']
    
    text_lower = text.lower()
    
    nl_count = sum(text_lower.count(kw) for kw in netherlands_keywords)
    eng_count = sum(text_lower.count(kw) for kw in england_keywords)
    
    if nl_count > eng_count:
        return 'Netherlands'
    elif eng_count > nl_count:
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
        
        base_min, plus_time = parse_minute(line)
        
        if base_min is not None:
            current_minute = base_min
            current_plus = plus_time
            
            i += 1
            if i < len(lines):
                commentary_text = lines[i].strip()
                
                if commentary_text:
                    entry = {
                        'match_id': 'netherlands_england',
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
    print("PARSING NETHERLANDS VS ENGLAND SEMI-FINAL")
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
    output_file = '../data/sports_mole_netherlands_england_commentary.csv'
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

