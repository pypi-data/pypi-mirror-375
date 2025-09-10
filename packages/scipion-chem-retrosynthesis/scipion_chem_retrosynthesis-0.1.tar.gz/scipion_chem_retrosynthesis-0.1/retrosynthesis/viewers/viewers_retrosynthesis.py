# **************************************************************************
# *
# * Authors:    Verónica Gamo
# *             Daniel Del Hoyo (ddelhoyo@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

import os, json, webbrowser

import pyworkflow.viewer as pwviewer
from pyworkflow.protocol import params

from retrosynthesis.protocols.protocol_retrosynthesis import ProtChemAiZynthFinder

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
        html_content = "<html><head><title>Data Visualization</title></head><body>"
        html_content += "<h1>Data Visualization</h1>"
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

class ImageViewer(pwviewer.Viewer):
    _label = 'Image Viewer'
    _environments = [pwviewer.DESKTOP_TKINTER]
    _targets = []

    def _visualize(self, image_files, **kwargs):
        for image_file in image_files:
            print(f"Opening image: {image_file}")
            os.system(f"xdg-open {image_file} &")


class ProtChemAiZynthFinderViewer(pwviewer.ProtocolViewer):
    """ Viewer for ProtChemAiZynthFinder protocol """
    _label = 'View JSON and Reactions'
    _targets = [ProtChemAiZynthFinder]

    def __init__(self, **args):
        super().__init__(**args)

    def _defineParams(self, form):
        form.addSection(label='View JSON and Images')
        group_json = form.addGroup('JSON Data')
        group_json.addParam('displayJson', params.LabelParam,
                            label='Open JSON file: ',
                            help='Show JSON data.')

        group_images = form.addGroup('Reactions')
        group_images.addParam('displayImages', params.LabelParam,
                              label='Open Images: ',
                              help='Show generated images.')

    def _getVisualizeDict(self):
        return {
            'displayJson': self._showJson,
            'displayImages': self._showImages,
        }

    def _showJson(self, paramName=None):
        json_file = self.getJsonFile()
        return JsonViewer(project=self.getProject())._visualize(json_file)

    def getJsonFile(self):
        return self.protocol._getExtraPath("output.json")
    

    def _showImages(self, paramName=None):
        images = self.getImageFiles()
        ImageViewer(project=self.getProject())._visualize(images)

    
    def getImageFiles(self):
        images = []
        extra_path = self.protocol._getExtraPath()

        for filename in os.listdir(extra_path):
            if filename.startswith("route") and filename.endswith(".png"):
                images.append(os.path.join(extra_path, filename))

        return images