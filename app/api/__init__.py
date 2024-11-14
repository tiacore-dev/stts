from flask_restx import Api
from .namespaces.analysis_ns import analysis_ns
from .namespaces.transcription_ns import transcription_ns

def register_namespaces(api: Api):
    api.add_namespace(analysis_ns)
    api.add_namespace(transcription_ns)