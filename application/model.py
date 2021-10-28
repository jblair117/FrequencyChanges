from application import detector
import re

def check_upload_file(filename):
    return detector.check_upload_file(filename)

def get_paths(upload_folder, files):
    return detector.get_paths(upload_folder, files)

def get_log(log_path):
    return detector.get_log(log_path)

def get_marking_name(marking):
    return detector.get_marking_name(marking)
    
def get_petri_net(net_path):
    return detector.get_petri_net(net_path)

def get_attributes_of_petri_net(net):
    return detector.get_attributes_of_petri_net(net)

def draw_petri_net(net, initial_marking, final_marking, places, arcs):
    return detector.draw_petri_net(net, initial_marking, final_marking, places, arcs)

def draw_save_petri_net_previews(net, initial_marking, final_marking, places, arcs, start, end):
    # valid_places = []
    invalid_places = []
    for p in places:
        tmp_gviz, count = detector.draw_petri_net_preview(net, initial_marking, final_marking, places, arcs, p.name)
        if p.name == start:
            detector.save_preview_petri_net(tmp_gviz, "START")
        elif p.name == end:
            detector.save_preview_petri_net(tmp_gviz, "END")
        else:
            detector.save_preview_petri_net(tmp_gviz, p.name)
        print(count)
        if count <= 2:
            invalid_places.append(p)
        # else:
        #     valid_places.append(p)
    # print(valid_places,invalid_places)
    return invalid_places


def save_visual(gviz):
    detector.save_visual(gviz)

def url_to_set(url):
    return detector.url_to_set(url)

def verify_files(files, upload_folder):
    return detector.verify_files(files, upload_folder)

def get_places(net):
    return detector.get_places(net)

def valid_places(places,target_place_ids):
    valid_places = {}
    invalid_places = []
    for target_id in target_place_ids:
        transitions_before_place, transitions_after_place, transitions_before_place_id, transitions_after_place_id, transitions_after_labels = detector.get_interesting_place_dets(places, target_id)
        if transitions_before_place != None:
            valid_places[target_id] = [transitions_before_place, transitions_after_place, transitions_before_place_id, transitions_after_place_id, transitions_after_labels]
            # print("valid_place",valid_places,type(valid_places))
        else:
            invalid_places.append(target_id)
    return valid_places, invalid_places

def select_places_calculation(log, net, initial_marking, final_marking, places,valid_places,pen,model):
    results = []
    sequences = []
    choice_sequences = []
    for k,v in valid_places.items():
        if v[0] != None:
            transitions_before_place_id = v[2]
            transitions_after_place_id = v[3]
            transitions_after_labels = v[4]
            # print("all",transitions_before_place_id,transitions_after_place_id,transitions_after_labels)
            sequence, choice_sequence = detector.create_trace_alignment(log, net, initial_marking, final_marking, transitions_before_place_id, transitions_after_place_id,
                                                            transitions_after_labels)
            result = detector.drift_detection(choice_sequence,pen,model)
            results.append(result)
            sequences.append(sequence)
            choice_sequences.append(choice_sequence)
    return results, sequences,choice_sequences

def get_drift_detection_results(results, sequences, valid):
    print_results = {}
    keys = list(valid.keys())
    for i in range(0, len(results)):
        print_result = detector.get_drift_detection_results(results[i], sequences[i])
        print_results[keys[i]] = print_result
    return print_results

def get_result_fig(choice_sequences, results):
    for i in range(0, len(results)):
        detector.save_result(choice_sequences[i], results[i])

def redo_places(places):
    return re.sub('[{},]', '', str(places)).replace(' ', ',')

def get_prototype_results(choice_sequence, result, net, place):
    return detector.get_prototype_prints_generalise(choice_sequence, result, net, place)
