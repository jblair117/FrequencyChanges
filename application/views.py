from application import app
from flask import render_template, request, redirect, url_for
from application import model

global files
global return_results
global prototype_results
global invalid
global select_pen
global select_model
# global valid_places
global invalid_places
global start
global end
# valid_places = []
invalid_places = []
return_results = []
invalid = []
select_pen = 0
select_model = ""

@app.route('/', methods = ['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            global files
            files = request.files.getlist("file")

            #check no file uploaad
            if files[0].filename == "":
                return render_template('upload.html', message ='No files uploaded. Please upload a .xes and .pnml file.')

            valid_count = model.verify_files(files, app.config['UPLOAD_FOLDER'])

            if(valid_count == 2):
                net_path, log_path = model.get_paths(app.config['UPLOAD_FOLDER'], files)
                net, initial_marking, final_marking = model.get_petri_net(net_path)

                global start
                start = model.get_marking_name(initial_marking)
                global end
                end = model.get_marking_name(final_marking)

                places, transitions, arcs = model.get_attributes_of_petri_net(net)
                gviz = model.draw_petri_net(net, initial_marking, final_marking, places, arcs)
                model.save_visual(gviz)
                # print("hi")
                # global valid_places
                global invalid_places
                invalid_places = model.draw_save_petri_net_previews(net, initial_marking, final_marking, places, arcs, start, end)
                print("Invalid places[0] is ----------", invalid_places[0])
                print(type(invalid_places[0]))
                # print("hi", valid_places,invalid_places)
                places_in_url = model.redo_places(places)
                return redirect(url_for('select_places'))
            else:
                return render_template('upload.html', message = "Invalid file type! Please Upload a .xes and .pnml file.")

        elif request.method == 'GET':
            return render_template('upload.html', message = "")
    except:
        return render_template('upload.html', message="An unexpected error occurred, you have been returned to the main menu. We apologise for any inconvenience.")

@app.route('/select_places', methods = ['GET', 'POST'])
def select_places():
    try:
        net_path, log_path = model.get_paths(app.config['UPLOAD_FOLDER'], files)
        log = model.get_log(log_path)
        net, initial_marking, final_marking = model.get_petri_net(net_path)
        p, transitions, arcs = model.get_attributes_of_petri_net(net)

        global start
        global end

        pf = f"{p}"
        start_brace = "{"
        end_brace = "}"
        ps = pf.replace(f"{start_brace}{start}", "{START") \
            .replace(f"{start_brace}{end}", "{END") \
            .replace(f"{start}{end_brace}", "START}") \
            .replace(f"{end}{end_brace}", "END}") \
            .replace(f"{start},", "START,") \
            .replace(f"{end},", "END,")

        invalid_placesf = f"{invalid_places}"
        invalid_placess = invalid_placesf.replace(f"[{start}", "[START") \
            .replace(f"[{end}", "[END") \
            .replace(f"{start}]", "START]") \
            .replace(f"{end}]", "END]") \
            .replace(f"{start},", "START,") \
            .replace(f"{end},", "END,")

        if request.method == 'POST':
            str_select_places = request.form['select_places']
            select_places = str_select_places.split(",")
            print("SELECT PLACES IS ---....----", select_places)

            for i in range(len(select_places)):
                if select_places[i] == "START":
                    select_places[i] = start
                elif select_places[i] == "END":
                    select_places[i] = end

            global select_pen
            global select_model
            select_pen = int(request.form['PenInputName'])
            select_model = str(request.form['modelSelect'])
            # print(select_pen, type(select_pen))
            # print(select_model, type(select_model))
            global invalid
            valid, invalid = model.valid_places(p, select_places)
            if len(invalid) > 0 and len(valid) == 0:
                return render_template('petri_net.html', places = ps, invalid_places = invalid_placess, message = "The place you entered is invalid. Please Try Again.")
            if len(valid) > 1:
                return render_template('petri_net.html', places = ps, invalid_places = invalid_placess, message = "You entered more than one place, please enter only one.")
            if len(valid) == 1:
                global return_results
                results, sequences, choice_sequences = model.select_places_calculation(log, net, initial_marking, final_marking, p, valid, select_pen,select_model)
                return_results = model.get_drift_detection_results(results, sequences,valid)
                model.get_result_fig(choice_sequences, results)
                global prototype_results
                prototype_results = model.get_prototype_results(choice_sequences[0], results[0], net, select_places[0])
                return redirect(url_for('show_results'))

        elif request.method == 'GET':
            # return render_template('petri_net.html', places=p, final_marking_name= final_marking_name, message = "Please Select Places")
            print("second", p, invalid_places)
            print("p is", p)
            print("invalid_places is", invalid_places)

            print("new p is", ps)
            print("new invalid_places is", invalid_placess)
            return render_template('petri_net.html', places = ps, invalid_places = invalid_placess, message = "")
    except:
        return render_template('upload.html', message="An unexpected error occurred, you have been returned to the main menu. We apologise for any inconvenience.")


@app.route('/results', methods = ['GET'])
def show_results():
    try:
        if len(return_results) == 0 and len(invalid) == 0:
            return render_template('upload.html', message="For an odd reason, we did not end up having a place to display at the end. Please try again.")

        else:
            places = list(return_results.keys())
            place = places[0]
            print("THE FINAL PLACE TO SHOW IS", place)
            print(type(place))
            message = return_results[place]
            collection = []

            for m in message:
                split_m = m.replace(',', '').split(' ')
                tmp = []
                tmp.append(split_m[5])
                tmp.append(split_m[8])
                tmp.append(split_m[9])
                collection.append(tmp)

            identities = []
            if(len(prototype_results) != 0):
                for i in range(len(prototype_results[0])):
                    identities.append(f"Transition {i+1}")
            else:
                identities = ''

            global start
            global end
            if place == start:
                place = "START"
            if place == end:
                place = "END"

            return render_template("results.html",
                               place=place,
                               collection=collection,
                               prototype_results=prototype_results,
                               identities=identities,
                               select_pen=select_pen,
                               select_model=select_model)
    except:
        return render_template('upload.html', message="An unexpected error occurred, you have been returned to the main menu. We apologise for any inconvenience.")
