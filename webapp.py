import json
import os
from flask import Flask, render_template, redirect, url_for, request
from threading import Thread

scrapper = Flask(__name__)

@scrapper.route("/<page_option>")
def load_data(page_option="chefs"):
 with open(page_option + '.json', 'r') as data:
  extracted_data = json.loads(data.read())
  data.close()
  return render_template("index.html", members=extracted_data["members"], page_option=page_option)

@scrapper.route("/")
def homepage():
 return redirect("/chefs")

@scrapper.route("/note", methods=['POST'])
def updateNote():
 note = request.form['note']
 file_name = request.form['category'] + '.json'
 selected_index = int(request.form['index']) - 1

 update_thread = Thread(target=updateFile, args=(file_name, note, selected_index))
 update_thread.daemon = True
 update_thread.start()

 return "done"

def updateFile(file_name, note, selected_index):
  with open(file_name, 'r') as data:
    extracted_data = json.loads(data.read())["members"]
    extracted_data[selected_index]['note'] = note
    data.close()

  os.remove(file_name)
  with open(file_name, 'w') as f:
    data_to_save = { 'members':  extracted_data}
    json.dump(data_to_save, f, indent=4)
    f.close()

if __name__ == '__main__':
	scrapper.run(port=8181, debug=True)
