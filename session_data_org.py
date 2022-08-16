import json
import os
import warnings
from pprint import pprint

KEYWORDS = {
    "1_farm_animals": [ "duck", "ewe", "hear", "howl", "cow", "beard", "goat", "sausage", "carts", "horse", "barn", "pool",
        "hay", "claws", "sharpen", "wool", "horns", "paw","woolly", "roots", "shear", "farm", "chicken", "gallop", "lamb", "mouse",
        "snout", "whistle", "pork", "farmer", "pig", "feathers"],
    "2_the_legend_of_the_bluebonnet": [ "scoop","feathers","dancer","family","burn","juice", "sound","council","shadow","thrust","berry",
        "doll","drought","flame","bone","comanche","handful","texas","warrior", "leggings","plentiful","wake","shaman","fill","belt","beaded","twig","listen",
        "circle","gathering","blanket","alone","quietly","polished","sign","word","heart","drum","glow","miraculous","camp","ash"],
    "3_the_little_house": ["brook","city","frost","carriage","pull","ripen","follow","leaves","countryside","light","garden","quiet","bud","automobile","crowded","daisy","bright","apartment","dump",
        "harvest","gold","garage","apple","moonlight","coast","pool","road","blossom","fields"],
    "4_the_little_house": ["grandmother","paint","quiet","dream","apple","light","cracked","lovely","apartment","husband","road","frightened","cellar","crooked","fields","moonlight","daisy",
        "place","lonely","mover","bright","dirty","happily","glance","city","dust"],
    "5_homes_around_the_world": ["ramp","fold","tongkonans","bamboo","stilt","jungle","tent","beehive","carved","container","alien","cave","wooden","toraja","boardwalk","ship","heated","strong","shape","school","fishermen",
        "treehouse","spaceship","block","house","ground","rock","lake","planet","adobe","clay","warm","reed","material","bubble","bricks","igloo","float"],
    "6_helpers_in_my_community": ["crossing guard","cement mixer","teacher","doctor","digger","helper","bulldozer","principal","librarian","crane","community","plumber","nurse","electrician","caretaker"],
    "7_helpers_in_my_community": ["rescue","nurse","ambulance","doctor","emergency","dentist","medical","police officer","firefighter","hospital","helper","protect","paramedic"],
    "8_from_sheep_to_sweater": ["healthy","grass","farm","straw","comb","bug","sweater","liquid","hay","dark","shape","rainbow","knit","color","store","truck","mud","wool","fleece",
        "mixture","shopper","wash","needle","twist"]
}

def get_all_sessions_by_child(data_path):

    if not os.path.isdir(data_path):
        warnings.warn("Path provided is not dir: " + data_path)
        return []

    all_sessions = [session for session in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, session))]
    all_sessions.sort(key=lambda x: x.split('_')[-1])
    return all_sessions

def read_json_files(data_path):

    if not os.path.exists(data_path):
        warnings.warn("Data path does not exists: " + data_path)
        return []
    
    with open(data_path, 'r') as f:
        data = json.load(f)
    
    return data

def get_story_id(story_name, end_page):
    story_session_database = {
        "geraldine_the_music_mouse_14": "0_geraldine_the_music_mouse",
        "farm_animals_11": "1_farm_animals",
        "the_legend_of_the_bluebonnet_14": "2_the_legend_of_the_bluebonnet",
        "the_little_house_12": "3_the_little_house",
        "the_little_house_23": "4_the_little_house",
        "homes_around_the_world_14": "5_homes_around_the_world",
        "helpers_in_my_community_10": "6_helpers_in_my_community",
        "helpers_in_my_community_20": "7_helpers_in_my_community",
        "from_sheep_to_sweater_11": "8_from_sheep_to_sweater"
    }
    return story_session_database[story_name + '_' + str(end_page)]


if __name__ == "__main__":

    # Resolving each participant's session data into one
    DATA_DIR = os.path.join(os.getcwd(), "data")
    OUTPUT_DIR = os.path.join(os.getcwd(), "output")
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    all_participants = [child for child in os.listdir(DATA_DIR) if os.path.isdir(os.path.join(DATA_DIR, child)) and child.startswith('c')]
    all_participants.sort()
    print(all_participants)

    for child in all_participants:
        
        child_path = os.path.join(DATA_DIR, child)
        # Step 1: Get all sessions from that child and order by date
        child_sessions = get_all_sessions_by_child(child_path)
        # print('\n'.join(child_sessions))

        # Step 2: Read the message json file with each session
        complete_session_logs = []
        for session in child_sessions:
            session_json = read_json_files(os.path.join(child_path, session, "messages.json")) 
            complete_session_logs += session_json
        print("Child %s has %d messages"%(child, len(complete_session_logs)))      

        # Step 3: Find all the starting index and ending index for each storybook
        storybook_info = dict()
        current_tracking_story = None
        decoding = 0
        explanation = 0
        current_page = -1
        page_activity = {
            "page": current_page,
            "activity": []
        }
        for message_idx in range(len(complete_session_logs)):
            message = complete_session_logs[message_idx]
            # print(message)
            if message['command'] == 'HELLO WORLD MSG':
                # might be a new story, find story's name
                story_segment = json.loads(message['msgs']['segments'][0])
                story_name = story_segment['segment_identifier']
                start_page = story_segment['start_page']
                end_page = story_segment['end_page']
                story_id = get_story_id(story_name, end_page)
                if story_id not in storybook_info.keys():
                    # If currently tracking a story, update the ending msg idx
                    if current_tracking_story != None:
                        storybook_info[current_tracking_story[1]]['ending_msg_idx'] = message_idx - 1
                        if page_activity['page'] != -1:
                            storybook_info[current_tracking_story[1]]['page_activities'].append(page_activity)
                    
                    current_page = -1
                    page_activity = {
                        "page": current_page,
                        "activity": []
                    }
                    storybook_info[story_id] = {
                        'story_name': story_name,
                        'start_page': start_page,
                        'end_page': end_page,
                        'starting_msg_idx': message_idx,
                        'ending_msg_idx': -1,
                        'pages': [],
                        'page_activities': [],
                        'pre_assessment': dict(),
                        'post_assessment': dict()
                    }
                    current_tracking_story = (story_name, story_id)
            elif message['command'] == 'page info':
                # find page number and record
                page_num = message['msgs']['page_num']
                if message['msgs']['storybook'] == current_tracking_story[0]:
                    storybook_info[current_tracking_story[1]]['pages'].append(page_num)
                    if page_activity['page'] != -1:
                        storybook_info[current_tracking_story[1]]['page_activities'].append(page_activity)
                    current_page = page_num
                    page_activity = {
                        "page": current_page,
                        "activity": []
                    }
            elif message['command'] == 'KEYWORD_ASSESSMENT_RESULT':
                assessment_result = message['msgs']
                if not assessment_result['has_assessment']:
                    continue
                keyword = assessment_result['keyword'][0]
                if not current_tracking_story[1].startswith('0') and keyword not in KEYWORDS[current_tracking_story[1]]:
                    continue
                if assessment_result['pre_session']:
                    if keyword in storybook_info[current_tracking_story[1]]['pre_assessment'].keys():
                        continue
                    else:
                        storybook_info[current_tracking_story[1]]['pre_assessment'][keyword] = assessment_result['correct']
                else:
                    if keyword in storybook_info[current_tracking_story[1]]['post_assessment'].keys():
                        continue
                    else:
                        storybook_info[current_tracking_story[1]]['post_assessment'][keyword] = assessment_result['correct']
            else:
                if current_page == -1:
                    continue
                # What happened on page
                activity = {
                    "type": "",
                    "Child": False,
                    "date_str": "",
                    "notes": ""
                }
                if message['command'] == 'SCREEN_TAPPING':
                    next_message = complete_session_logs[message_idx + 1]
                    last_message = complete_session_logs[message_idx - 1]
                    # print(next_message)
                    if next_message['command'] == "WORD_TAPPED":
                        activity['type'] = "WORD_TAPPED"
                        activity['date_str'] = next_message['date_str']
                        activity['Child'] = True
                        activity['notes'] = next_message['msgs']
                        # print(complete_session_logs[message_idx + 2])
                    elif next_message['command'] == "SCENE_OBJECT_TAPPED":
                        activity['type'] = "SCENE_OBJECT_TAPPED"
                        activity['date_str'] = next_message['date_str']
                        activity['Child'] = True
                        activity['notes'] = next_message['msgs']
                    elif next_message['command'] == "SENTENCE_SWIPED":
                        activity['type'] = "AUDIO_PLAYED"
                        activity['date_str'] = next_message['date_str']
                        activity['Child'] = True
                        activity['notes'] = next_message['msgs']
                    elif next_message['command'] == "JIBO_QUESTION_BUTTON_PRESSED":
                        activity['type'] = "JIBO_QUESTION_REQUESTED"
                        activity['date_str'] = next_message['date_str']
                        activity['Child'] = True
                        activity['notes'] = "Jibo Interaction Start"
                    elif next_message['command'] == "WORD_DECODING_PANEL_OPEN":
                        activity['type'] = "CHILD_EXPLORE"
                        activity['date_str'] = next_message['date_str']
                        activity['Child'] = True
                        activity['notes'] = "Child Click on a Keyword"
                    elif next_message['command'] == "WORD_DECODING_SOUND_OUT_COMPLETE":
                        activity['type'] = "CHILD_DECODING_INTERACTION"
                        activity['date_str'] = next_message['date_str']
                        activity['Child'] = True
                        activity['notes'] = "Child Learn Decoding"
                    elif next_message['command'] == "WORD_EXPLANATION_COMPLETE":
                        activity['type'] = "CHILD_EXPLANATION_INTERACTION"
                        activity['date_str'] = next_message['date_str']
                        activity['Child'] = True
                        activity['notes'] = "Child Learn Explanation"
                elif message['command'] == "JIBO_QUESTION_ASKING_ACTIVITY":
                    if message['msgs']['enable_button']:
                        activity['type'] = "JIBO_QUESTION_END"
                    else:
                        activity['type'] = "JIBO_QUESTION_START"
                    activity['date_str'] = message['date_str']
                    activity['Child'] = False
                elif message['command'] == "JIBO_VIRTUAL_ACTION":
                    if message['msgs']['button'] == "open":
                        activity['type'] = "JIBO_OPEN_PANEL"
                    elif message['msgs']['button'] == "speaker":
                        activity['type'] = "JIBO_DECODING"
                    elif message['msgs']['button'] == "dictionary":
                        activity['type'] = "JIBO_EXPLANATION"
                    activity['date_str'] = message['date_str']
                    activity['Child'] = False
                    activity['notes'] = message['msgs']
                    

                # elif message['command'] == 'JIBO_QUESTION_ASKING_ACTIVITY':
                    # print(message)
                if activity['type'] != "":
                    page_activity['activity'].append(activity)

                # if current_tracking_story != None:
                #     storybook_info[current_tracking_story[1]]['screen_tapping'].append(new_taps)
            # elif message['command'] == 'WORD_DECODING_SOUND_OUT_COMPLETE':
            #     decoding += 1
            #     # break
            # elif message['command'] == 'WORD_EXPLANATION_COMPLETE':
            #     explanation += 1
            #     break

        child_output_path = os.path.join(OUTPUT_DIR, child + ".json")
        with open(child_output_path, 'w') as f:
            json.dump(storybook_info, f, indent=4)

        # log the current child's story history
        # pprint(storybook_info)
        # org = list(set(tapping_types))
        # org_dict = dict()
        # for tap in org:
        #     if tap[1] not in org_dict.keys():
        #         org_dict[tap[1]] = []
            
        #     org_dict[tap[1]] = list(set(org_dict[tap[1]] + [tap[0]]))
        
        # for k, v in org_dict.items():
        #     print("When tap is " + k)
        #     print("\t", v)
        #     print("\n")

        
        # Step 4: Display the activity, find the cues to recognize, and order children's behaviors within each storybook and within each page
