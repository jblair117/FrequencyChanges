import os
import re
import numpy as np
import matplotlib.pyplot as plt
import ruptures as rpt
from matplotlib import pylab
from pylab import *


from werkzeug.utils import secure_filename

from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.objects.petri_net.importer import importer as pnml_importer
from pm4py.algo.conformance.alignments.petri_net import algorithm as alignments
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter
from pm4py.visualization.petri_net.common.visualize import graphviz_visualization
from pm4py.visualization.petri_net import visualizer as pn_visualizer

def getTime(elem):
    return elem[0]

def get_petri_net(net_path):
    net, initial_marking, final_marking = pnml_importer.apply(net_path)
    return net, initial_marking, final_marking

def get_log(log_path):
    log = xes_importer.apply(os.path.join(log_path))
    return log

def get_attributes_of_petri_net(net):
    places = net.places
    transitions = net.transitions
    arcs = net.arcs
    return places, transitions, arcs

def get_marking_name(marking):
    repr_string = marking.__repr__()
    marking_name = re.sub('[\[\]\'\']', '', repr_string).split(':')[0]
    return marking_name

"""
Draw the Petri Net
"""
def draw_petri_net(net, initial_marking, final_marking, places, arcs):
    deco = {}
    for i in arcs:
            deco[i] = {"color":"red"}
    initial_place_name = get_marking_name(initial_marking)
    final_place_name = get_marking_name(final_marking)

    for place in places:
        if place.name == initial_place_name:
            deco[place] = {"label": place.name, "color": "green"}
        elif place.name == final_place_name:
            deco[place] = {"label": place.name, "color": "orange"}
        else:
            deco[place] = {"label":place.name,"color":"yellow"}

    # pnml_exporter.apply(net, initial_marking, "test_files/createdPetriNet1.pnml", final_marking=final_marking)
    gviz = graphviz_visualization(net, image_format='png', initial_marking=None,
    final_marking=None, decorations=deco, debug=False, set_rankdir=None)
    return gviz

def draw_petri_net_preview(net, initial_marking, final_marking, places, arcs, preview_place):
    all_deco = {}

    count = 1
    for i in arcs:
        if i.source.name == preview_place:
            all_deco[i] = {"label": str(count), "penwidth":'2'}
            count += 1
        else:
            all_deco[i] = {"color":"red"}
    initial_place_name = get_marking_name(initial_marking)
    final_place_name = get_marking_name(final_marking)

    for place in places:
        if place.name == initial_place_name:
            all_deco[place] = {"label": place.name, "color": "green"}
        elif place.name == final_place_name:
            all_deco[place] = {"label": place.name, "color": "orange"}
        else:
            all_deco[place] = {"label":place.name,"color":"yellow"}

    gviz = graphviz_visualization(net, image_format='png', initial_marking=None,
    final_marking=None, decorations=all_deco, debug=False, set_rankdir=None)
    return gviz

def save_petri_net(gviz):
    filename = 'saved_drawings/petri_net'
    gviz.render(filename=filename)
    pylab.savefig(filename)

def save_preview_petri_net(gviz,image_name):
    filename = "application/static/image/" + str(image_name) + ".png"
    pn_visualizer.save(gviz, filename)
"""
Yang's code starts here again
"""
def get_interesting_place_dets(places, target_place_id):
    transitions_before_place = set()
    transitions_after_place = set()
    transitions_before_place_id = set()
    transitions_after_place_id = set()
    transitions_after_labels = {}
    counter = 1

    for p in places:
        #print(p.name)
        if p.name == target_place_id:
            if len(p.out_arcs) == 1:
                return [None,None,None,None,None]
                # break
            else:
                for arc in p.in_arcs:
                    transitions_before_place.add(arc.source)
                    transitions_before_place_id.add(arc.source.name)
                for arc in p.out_arcs:
                    transitions_after_place.add(arc.target)
                    transitions_after_place_id.add(arc.target.name)
                    transitions_after_labels.update({arc.target.name: counter})
                    counter = counter + 1

    if len(transitions_after_place) == 0:
        return [None,None,None,None,None]

    return transitions_before_place, transitions_after_place, transitions_before_place_id, transitions_after_place_id, transitions_after_labels

def print_sanity_checks(target_place_id, transitions_before_place, transitions_after_place, transitions_after_labels):
    print("The place you selected is: " + target_place_id)
    print("The input transitions are: ")
    for t in transitions_before_place:
        if t.label == None:
            print("Transition id: " + t.name + ", Label: hidden")
        else:
            print("Transition id: " + t.name + ", Label: " + t.label)

    print("The output transitions are: ")
    for t in transitions_after_place:
        if t.label == None:
            print("Transition id: " + t.name + ", Label: hidden" + ", Choice: " + str(transitions_after_labels[t.name]))
        else:
            print("Transition id: " + t.name + ", Label: " + t.label + ", Choice: " + str(
                transitions_after_labels[t.name]))


def create_trace_alignment(log, net, initial_marking, final_marking, transitions_before_place_id, transitions_after_place_id, transitions_after_labels):
    parameters = {alignments.Parameters.PARAM_ALIGNMENT_RESULT_IS_SYNC_PROD_AWARE:"True"}
    aligned_traces = alignments.apply_log(log, net, initial_marking, final_marking, parameters=parameters)

    sequence = []
    choice_sequence = np.array([[99],[100]])
    choice_sequence_trace_index = {}
    points_counter = 0
    traces_counter = -1
    for aligned_trace in aligned_traces:
        trace_move = -1
        traces_counter = traces_counter + 1
        find_before = False
        alignment = aligned_trace["alignment"]
        #print(alignment)
        for i in range (0, len(alignment)):
        #for i in range (0, 1):
            if alignment[i][0][0] != ">>":
                trace_move = trace_move + 1
                #print(alignment[i][0][0])
                #print(trace_move)
            if alignment[i][0][1] == ">>":
                continue
            if alignment[i][0][1] in transitions_before_place_id:
                find_before = True
            if alignment[i][0][1] in transitions_after_place_id and find_before:
                t_name = alignment[i][0][1]
                value = transitions_after_labels[t_name]
                #choice_sequence = np.concatenate((choice_sequence, np.array([[value]])), axis=0)
                #choice_sequence_trace_index.update({points_counter: traces_counter})
                if alignment[i][0][0] != ">>":
                    sequence.append([log[traces_counter][trace_move - 1]["time:timestamp"], value])
                else:
                    sequence.append([log[traces_counter][trace_move]["time:timestamp"], value])

                points_counter = points_counter + 1
                find_before = False

    sequence.sort(key=getTime)

    for item in sequence:
        choice_sequence = np.concatenate((choice_sequence, np.array([[item[1]]])), axis=0)
    choice_sequence = np.delete(choice_sequence, 0, axis = 0)
    choice_sequence = np.delete(choice_sequence, 0, axis = 0)

    return sequence, choice_sequence

def drift_detection(choice_sequence, pen_value,model_type):
    print("CHOICE SEQUENCE\n\n\n\n\n", len(choice_sequence))
    c = rpt.costs.CostRbf()
    algo = rpt.Pelt(model=model_type, custom_cost=c).fit(choice_sequence)
    result = algo.predict(pen = pen_value)
    # result = algo.predict(pen = 5)
    # print(test_sequence_1)
    # print(choice_sequence[1][0])
    # print(choice_sequence)
    print("CHOICE SEQUENCE\n\n\n\n\n", len(choice_sequence))
    return result

def print_drift_detection_results(result, sequence):
    for i in range(0, len(result) - 1):
       print("Concept drift detected at point " + str(result[i]) + ", at trace " + str(sequence[result[i] - 1][0]))

def get_drift_detection_results(result, sequence):
    print_results = []
    print("function")
    for i in range(0, len(result)):
       print_results.append("Concept drift detected at point " + str(result[i]) + ", at trace " + str(sequence[result[i] - 1][0]))
    print("result",result)
    return print_results

#Prototype only, should modify the code below if using another model and log
'''
def get_prototype_prints(choice_sequence, result):

    results = []

    A = 0
    B = 0
    C = 0

    for i in range(0, result[0]):
        if choice_sequence[i][0] == 1:
            A = A + 1
        if choice_sequence[i][0] == 2:
            B = B + 1
        if choice_sequence[i][0] == 3:
            C = C + 1


    total = result[0]
    adder = []
    adder.append(str(A / total))
    adder.append(str(B / total))
    adder.append(str(C / total))

    results.append(adder)

    A = 0
    B = 0
    C = 0

    for i in range(result[0], result[1]):
        if choice_sequence[i][0] == 1:
            A = A + 1
        if choice_sequence[i][0] == 2:
            B = B + 1
        if choice_sequence[i][0] == 3:
            C = C + 1


    total = result[1] - result[0]
    adder = []
    adder.append(str(A / total))
    adder.append(str(B / total))
    adder.append(str(C / total))

    results.append(adder)

    A = 0
    B = 0
    C = 0

    for i in range(result[1], len(choice_sequence)):
        if choice_sequence[i][0] == 1:
            A = A + 1
        if choice_sequence[i][0] == 2:
            B = B + 1
        if choice_sequence[i][0] == 3:
            C = C + 1


    total = len(choice_sequence) - result[1]
    adder = []
    adder.append(str(A / total))
    adder.append(str(B / total))
    adder.append(str(C / total))

    results.append(adder)

    return results
'''
def get_prototype_prints_generalise(choice_sequence, result, net, place):

    a, b, c, d, e = get_interesting_place_dets(net.places, place)
    num = len(b)
    print("NUM ISSSS.....", num)

    results = []
    values = [0 for _ in range(num)]

    for i in range(0, result[0]):
        val = choice_sequence[i][0]
        values[val - 1] += 1

    total = result[0]
    adder = []
    for i in values:
        adder.append(str(i / total))
    results.append(adder)

    values = [0 for _ in range(num)]
    for i in range(result[0], result[1]):
        val = choice_sequence[i][0]
        values[val - 1] += 1

    total = result[1] - result[0]
    adder = []
    for i in values:
        adder.append(str(i / total))
    results.append(adder)

    values = [0 for _ in range(num)]
    for i in range(result[1], len(choice_sequence)):
        val = choice_sequence[i][0]
        values[val - 1] += 1

    total = len(choice_sequence) - result[1]
    adder = []
    for i in values:
        adder.append(str(i / total))
    results.append(adder)

    return results


def check_upload_file(filename):
    ALLOWED_EXTENSIONS = {"xes", "pnml"}
    file_type = filename.rsplit(".")[1]
    if file_type in ALLOWED_EXTENSIONS:
        return True
    return False

'''
def main():
    net_path = "test_files/helpdesk.pnml"
    log_path = "test_files/helpdesk.xes"

    net, initial_marking, final_marking = get_petri_net(net_path)
    log = get_log(log_path)

    places, transitions, arcs = get_attributes_of_petri_net(net)

    gviz = draw_petri_net(net, initial_marking, final_marking, places, arcs)
    save_petri_net(gviz)
    pn_visualizer.view(gviz)

    net, initial_marking, final_marking = pnml_importer.apply(net_path)

    """
    Input
    """
    target_place_ids = ["n1","n5"]

    for target_id in target_place_ids:
        transitions_before_place, transitions_after_place, transitions_before_place_id, transitions_after_place_id, transitions_after_labels = get_interesting_place_dets(places, target_id)
        # print(transitions_before_place, transitions_after_place, transitions_before_place_id, transitions_after_place_id, transitions_after_labels)
        if transitions_before_place != None:
            print_sanity_checks(target_id, transitions_before_place, transitions_after_place, transitions_after_labels)

            sequence, choice_sequence = create_trace_alignment(log, net, initial_marking, final_marking, transitions_before_place_id, transitions_after_place_id,
                                                            transitions_after_labels)
            result = drift_detection(choice_sequence)
            # print_drift_detection_results(result, sequence)
    
    print("currently done")

    """
    we need some modification on this 
    comment this for now
    """
    # prototype_prints(choice_sequence, result)

    # rpt.display(choice_sequence, result)
    # plt.show()
'''

def get_paths(path, files):
    if files[0].filename.rsplit(".")[1] == "xes":
        log_path = os.path.join (path,files[0].filename)
        net_path = os.path.join (path,files[1].filename)
    else:
        log_path = os.path.join (path,files[1].filename)
        net_path = os.path.join (path,files[0].filename)

    return net_path, log_path

def generate_input(path, files):

    net_path, log_path = get_paths(path, files)
    net, initial_marking, final_marking = get_petri_net(net_path)
    places, transitions, arcs = get_attributes_of_petri_net(net)

    gviz = draw_petri_net(net, initial_marking, final_marking, places, arcs)
    pn_visualizer.save(gviz, "application/static/image/petri_net.png")

    return places


def save_visual(gviz):
    pn_visualizer.save(gviz, "application/static/image/petri_net.png")

def save_result(choice_sequence, result):
    rpt.display(choice_sequence, result)
    plt.savefig("application/static/image/results.png")
    # plt.show()

def url_to_set(url):
    s = set()
    split_url = url.split('-')
    for i in split_url:
        s.add(i)

    return s

def verify_files(files, upload_folder):
    valid_count = 0
    for i in files:
        valid_file = check_upload_file(i.filename)
        # check the file type
        if (valid_file):
            valid_count += 1
            i.save(os.path.join(upload_folder, secure_filename(i.filename)))

    return valid_count

def get_places(net):
    return net.places





