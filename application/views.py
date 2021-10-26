from application import app
from flask import render_template, request, redirect, url_for
from application import model
import os
import re

global files
global return_results
global invalid
global select_pen
global select_model
return_results = []
invalid = []
select_pen = 0
select_model = ""

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        global files
        files = request.files.getlist("file")

        #check no file uploaad
        if files[0].filename == "":
            return render_template('upload.html', message ='No selected file. Please Upload .xes and .pnml files.')
        valid_count =  model.verify_files(files, app.config['UPLOAD_FOLDER'])

        if(valid_count == 2):
            net_path, log_path = model.get_paths(app.config['UPLOAD_FOLDER'], files)
            net, initial_marking, final_marking = model.get_petri_net(net_path)
            places, transitions, arcs = model.get_attributes_of_petri_net(net)
            gviz = model.draw_petri_net(net, initial_marking, final_marking, places, arcs)
            model.save_visual(gviz)
            model.draw_save_petri_net_previews(net, initial_marking, final_marking, places, arcs)
            places_in_url = model.redo_places(places)
            return redirect(url_for('select_places'))
        else:
            return render_template('upload.html', message = "Invalid file type! Please Upload .xes and .pnml files")

    elif request.method == 'GET':
        return render_template('upload.html', message = "Process Mining <br> Branching Frequency Changes")

@app.route('/select_places', methods = ['GET', 'POST'])
def select_places():
    net_path, log_path = model.get_paths(app.config['UPLOAD_FOLDER'], files)
    log = model.get_log(log_path)
    net, initial_marking, final_marking = model.get_petri_net(net_path)
    p, transitions, arcs = model.get_attributes_of_petri_net(net)
    final_marking_name = model.get_marking_name(final_marking)

    if request.method == 'POST':
        str_select_places = request.form['select_places'] 
        select_places = str_select_places.split(",")
        global select_pen
        global select_model
        select_pen = int(request.form['PenInputName'])
        select_model = str(request.form['modelSelect'])
        print(select_pen, type(select_pen))
        print(select_model, type(select_model))
        global invalid
        valid, invalid = model.valid_places(p,select_places)
        if len(invalid) > 0 and len(valid) == 0:
            return render_template('petri_net.html', places=model.redo_places(p), message = "The entered places are invalid. Please Try Again.")
        if len(valid) > 0:
            global return_results
            results, sequences, choice_sequences = model.select_places_calculation(log, net, initial_marking, final_marking, p, valid, select_pen,select_model)
            return_results = model.get_drift_detection_results(results, sequences,valid)
            model.get_result_fig (choice_sequences, results)
            return redirect(url_for('show_results'))

    elif request.method == 'GET':
        return render_template('petri_net.html', places=p, final_marking_name= final_marking_name, message = "Please Select Places")

@app.route('/results', methods = ['GET'])
def show_results():
    if len(return_results) == 0 and len(invalid) == 0:
        return "error"
    else:
        return render_template("results.html", return_results = return_results, invalid = invalid, select_pen = select_pen, select_model = select_model)
