import json
import warnings
import os
import pandas as pd

def get_child_group(child_id, group):

    child_group = ""
    for k, v in group.items():
        if child_id in v:
            child_group = k
    if child_group == "":
        warnings.warn("Cannot find children's group: " + child_id)
        print(group)
    return child_group

def get_child_session_data(data_path):
    if not os.path.isfile(data_path):
        warnings.warn("Child file not found: " + data_path)
        return None
    
    with open(data_path, 'r') as f:
        data = json.load(f)
    return data

def get_session_aggregated(session_data):

    all_column = list(session_data[0].keys())
    if 'page_num' in all_column:
        all_column.remove('page_num')
    df = pd.DataFrame(session_data)
    sum_data = df[all_column].sum()
    session_summary = dict()
    for col in all_column:
        session_summary[col + "_sum"] = int(sum_data[col])
        # session_summary[col + "_avg"] = avg_data[col]
    session_summary['total_sum'] = int(sum_data.sum())
    return session_summary

if __name__ == "__main__":

    CHILD_GAME_DIR = os.path.join(os.getcwd(), "output")
    # HARD CODED Child Conditions
    child_group_dataset = {
        "child-lead": ["c305", "c309", "c310", "c311", "c320", "c339", "c351", "c361", "c349", "c323",
        "c338", "c369", "c360", "c365", "c355", "c370", "c372", "c341", "c322"],
        "robot-lead": ["c301", "c304", "c306", "c319", "c336", "c346", "c354","c364", "c334", "c348",
        "c350", "c368", "c359", "c325", "c366", "c318", "c326"]
    }

    all_child = [child[:-5] for child in os.listdir(CHILD_GAME_DIR) if child.startswith("c3")]
    print(all_child)
    all_children_data = dict()
    for child in all_child:
        print("Calculating for child ", child)
        child_group = get_child_group(child, child_group_dataset)
        # For each child, read their session info
        child_data = get_child_session_data(os.path.join(CHILD_GAME_DIR, child + ".json"))

        child_result = dict()
        # Skip the first session
        for session_id, data in child_data.items():
            if session_id.startswith('0'):
                continue

            # assert len(data['pages']) == len(data['page_activities']), "Data length not the same: %s in %s (%d, %d)"%(child, session_id, len(data['pages']), len(data['page_activities']))
            # For each page in a story
            # 1. How many times child explored
            # 2. The exact number of exploration for each activity: Word Tap, SceneObj Tap, Audio, Explanation, Decoding, Robot Button (if child-lead and first/last sessions)
            child_session_result = []
            for page in data['page_activities']:
                page_result = {
                    "page_num": page['page'],
                    "word_tap": 0,
                    "sceneobj_tap": 0,
                    "audio_play": 0,
                    "explanation": 0,
                    "decoding": 0,
                    "robot_interaction": 0
                }

                treatment_condition = -1
                for activity in page['activity']:
                    if child_group == "robot_lead" and treatment_condition == -1:
                        treatment_condition = 0
                    
                    if treatment_condition == 0:
                        if activity['type'] == "JIBO_QUESTION_END":
                            treatment_condition = 1
                        else:
                            continue

                    robot_activity = False
                    if activity['type'] == "JIBO_QUESTION_REQUESTED":
                        robot_activity = True
                        page_result['robot_interaction'] += 1
                    elif activity['type'] == "JIBO_QUESTION_END":
                        robot_activity = False
                    else: 
                        if robot_activity:
                            continue
                        else:
                            if activity['type'] == "SCENE_OBJECT_TAPPED":
                                page_result['sceneobj_tap'] += 1
                            elif activity['type'] == "WORD_TAPPED":
                                page_result['word_tap'] += 1
                            elif activity['type'] == "AUDIO_PLAYED":
                                page_result['audio_play'] += 1
                            elif activity['type'] == "JIBO_QUESTION_REQUESTED":
                                page_result['robot_interaction'] += 1
                            elif activity['type'] == "CHILD_EXPLANATION_INTERACTION":
                                page_result['explanation'] += 1
                            elif activity['type'] == "CHILD_DECODING_INTERACTION":
                                page_result['decoding'] += 1

                child_session_result.append(page_result)

            if child_group == "child-lead":
                study_code = "control"
            else:
                study_code = "treatment"
            if session_id.startswith("1"):
                study_code += "-pre"
            elif session_id.startswith("8"):
                study_code += "-post"
            
            session_summary = get_session_aggregated(child_session_result)
            session_summary['total_avg'] = session_summary['total_sum']/len(data['page_activities'])
            child_result[session_id] = {
                "result": child_session_result,
                "study_code": study_code,
                "session_summary": session_summary
            }
        
        all_children_data[child] = child_result
    
    with open(os.path.join(CHILD_GAME_DIR, "children_exploration_results.json"), 'w') as f:
        json.dump(all_children_data, f, indent=4)

    # Making a pandas or csv file:
    all_child_sessions = []
    for child, sessions in all_children_data.items():
        for session_id, session_data in sessions.items():
            child_session = {
                "child_id": child,
                "session_id": session_id,
                "study_code": session_data['study_code'],
            }
            child_session.update(session_data['session_summary'])
            all_child_sessions.append(child_session)
    final_df = pd.DataFrame(all_child_sessions)
    print(final_df.head(5))
    final_df.to_csv(os.path.join(CHILD_GAME_DIR, "children_exploration_results.csv"))