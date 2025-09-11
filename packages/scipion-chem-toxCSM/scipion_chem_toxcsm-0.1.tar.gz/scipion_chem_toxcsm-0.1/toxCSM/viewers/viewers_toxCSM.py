import os
import json
import webbrowser
import pyworkflow.viewer as pwviewer
from pyworkflow.protocol import params
from toxCSM.protocols.protocol_toxCSM import ProtChemToxCSM


class JsonViewer(pwviewer.Viewer):
    _label = 'JSON Data Viewer'
    _environments = [pwviewer.DESKTOP_TKINTER]
    _targets = []

    def _visualize(self, json_file, **kwargs):
        json_path = os.path.abspath(json_file)
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        data = self.read_json(json_path)
        if not data:
            raise ValueError(f"No data found in JSON file: {json_path}")

        html_content = self.create_html(data)
        html_path = self.save_html(html_content, json_path)
        self.display_html(html_path)

    def read_json(self, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
        return data

    def create_html(self, data):
        html_content = "<html><head><title> Toxicity Prediction</title></head><body>"
        html_content += "<h1>Toxicity Prediction</h1>"
        html_content += "<pre>" + json.dumps(data, indent=4) + "</pre>"
        html_content += "</body></html>"
        return html_content

    def save_html(self, html_content, json_path):
        html_path = os.path.splitext(json_path)[0] + '.html'
        with open(html_path, 'w') as f:
            f.write(html_content)
        return html_path

    def display_html(self, html_path):
        webbrowser.open_new_tab(f'file://{os.path.realpath(html_path)}')


class ProtChemToxCSMViewer(pwviewer.ProtocolViewer):
    """ Viewer for ProtChemToxCSM Protocol """
    _label = 'View ToxCSM Analysis Results'
    _targets = [ProtChemToxCSM]

    def __init__(self, **args):
        super().__init__(**args)

    def _defineParams(self, form):
        form.addSection(label='ToxCSM Analysis Data')
        group_json = form.addGroup('JSON Data')
        group_json.addParam('displayJson', params.LabelParam,
                            label='Open JSON file: ',
                            help='Click to open and view the JSON data containing the ToxCSM results.')
        
        group_detail = form.addGroup('Detailed Information')
        group_detail.addParam('displayDetail', params.LabelParam,
                              label='View Detailed Information:',
                              help='Click to view more detailed information in the webpage')

    def _getVisualizeDict(self):
        return {
            'displayJson': self.showJson,
            'displayDetail': self.getDetailUrl
        }
    
    def getDetailUrl(self, paramName=None):
        filename='job_id.txt'
        txt_file=self.protocol._getExtraPath(filename)
        with open(txt_file, 'r') as file:
            job_id = file.read().strip()
        url = f"https://biosig.lab.uq.edu.au/toxcsm/prediction_results/{job_id}"
        webbrowser.open_new_tab(url)


    def showJson(self, paramName=None):
        json_file = self.getJsonFile()
        return JsonViewer(project=self.getProject())._visualize(json_file)

    def getJsonFile(self):
        return self.protocol._getExtraPath("toxCSM_results.json")
    