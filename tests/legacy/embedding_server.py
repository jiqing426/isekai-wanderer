"""Lightweight embedding HTTP server using sentence-transformers bge-small-zh-v1.5."""
import json
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from http.server import HTTPServer, BaseHTTPRequestHandler
from sentence_transformers import SentenceTransformer

print("Loading model...")
model = SentenceTransformer('BAAI/bge-small-zh-v1.5')
print(f"Model loaded, dim={model.get_sentence_embedding_dimension()}")

class EmbeddingHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/embed':
            self.send_error(404)
            return
        content_length = int(self.headers['Content-Length'])
        body = json.loads(self.rfile.read(content_length))
        texts = body.get('texts', [body.get('text', '')])
        vecs = model.encode(texts, normalize_embeddings=True)
        if len(texts) > 1:
            result = [v.tolist() for v in vecs]
        else:
            result = vecs[0].tolist()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'embedding': result, 'dim': model.get_sentence_embedding_dimension()}).encode())

    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        else:
            self.send_error(404)

server = HTTPServer(('0.0.0.0', 8084), EmbeddingHandler)
print("Embedding server on 0.0.0.0:8084")
server.serve_forever()
