import os
import uuid
import shutil
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_file, abort
from flask_restful import Resource, Api
#from rpviz.main import run
import rpReader
from io import BytesIO
import tarfile


app = Flask(__name__)
api = Api(app)
#dataFolder = os.path.join( os.path.dirname(__file__),  'data' )


#TODO: test that it works well
#declare the rpReader globally to avoid reading the pickle at every instance
rpreader = rpRanker.rpReader()


def stamp( data, status=1 ):
    appinfo = {'app': 'rpReader', 'version': '1.0', 
               'author': 'Melchior du Lac',
               'organization': 'BRS',
               'time': datetime.now().isoformat(), 
               'status': status}
    out = appinfo.copy()
    out['data'] = data
    return out


class RestApp( Resource ):
    """ REST App."""
    def post(self):
        return jsonify( stamp(None) )
    def get(self):
        return jsonify( stamp(None) )


class RestQuery(Resource):
    """ REST interface that generates the Design.
        Avoid returning numpy or pandas object in
        order to keep the client lighter.
    """
    def post(self):       
        rp2paths_compounds = request.files['rp2paths_compounds'].read()
        rp2paths_scope = request.files['rp2paths_scope'].read()
        rp2paths_outPaths = request.files['rp2paths_outPaths'].read()
        params = json.load(request.files['params'])
        #pass the files to the rpReader
        rpsbml_paths = rpreader.rp2ToSBML(rp2paths_compounds, 
                            rp2paths_scope, 
                            rp2paths_outPaths,
                            params['maxRuleIds'],
                            params['pathId'],
                            params['compartmentId'])
        #pass the SBML results to a tar
        if rpsbml_paths=={}:
            flask.abort(204)
        outTar = BytesIO()
        tf = tarfile.open(outTar, 'w:xz')
        for rpsbml_name in rpsbml_paths:
            data = libsbml.writeSBMLToString(rpsbml_paths[rpsbml_name].document).encode('utf-8')
            fiOut = BytesIO(data)
            info = tarfile.TarInfo(rpsbml_name)
            info.size = len(data)
            tf.addfile(tarinfo=info, fileobj=fiOut)
        return send_file(outTar, as_attachment=True)


api.add_resource(RestApp, '/REST')
api.add_resource(RestQuery, '/REST/Query')


if __name__== "__main__":
    debug = os.getenv('USER') == 'mdulac'
    app.run(host="0.0.0.0", port=8997, debug=debug, threaded=True)

