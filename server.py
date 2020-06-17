import http.server
import socketserver
import sqlite3
from urllib.parse import urlparse, parse_qs, unquote
import json

port = 8090
print('port = ',port)

def load_data():
  conn = sqlite3.connect('pays.sqlite')
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  c.execute("SELECT * FROM countries")
  data = c.fetchall()
  return data

class RequestHandler(http.server.SimpleHTTPRequestHandler):

  # sous-répertoire racine des documents statiques
  static_dir = '/client'
  # version du serveur
  server_version = 'final.py/0.1'
  # Chargement des données
  database = load_data()

  # On surcharge la méthode qui traite les requêtes GET
  def do_GET(self):
    self.init_params()

    # Requête location - retourne la liste de lieux et leurs coordonnées géogrpahiques
    if self.path_info[0] == "location":
      data = []
      for d in self.database:
        data.append({'wp': d['wp'], 'lat': d['lat'], 'lon': d['lon'], 'name': d['name']})
      self.send_json(data)

    # Requête description - retourne la description du lieu dont on passe l'id en paramètre dans l'URL
    elif self.path_info[0] == "description":
      for d in self.database:
        if d['wp'] == self.path_info[1]:
          self.send_json(dict(d))
          break

    else:
      self.send_static()

  # Méthode pour traiter les requêtes HEAD
  def do_HEAD(self):
    self.send_static()

  # On envoie le document statique demandé
  def send_static(self):

    # On modifie le chemin d'accès en insérant le répertoire préfixe
    self.path = self.static_dir + self.path

    # On appelle la méthode parent (do_GET ou do_HEAD)
    # à partir du verbe HTTP (GET ou HEAD)
    if (self.command == 'HEAD'):
        http.server.SimpleHTTPRequestHandler.do_HEAD(self)
    else:
        http.server.SimpleHTTPRequestHandler.do_GET(self)

  # On envoie un contenu encodé en json
  def send_json(self, data, headers=[]):
    body = bytes(json.dumps(data), 'utf-8') # encodage en json et UTF-8
    self.send_response(200)
    self.send_header('Content-Type', 'application/json')
    self.send_header('Content-Length', int(len(body)))
    [self.send_header(*t) for t in headers]
    self.end_headers()
    self.wfile.write(body)

  # On envoie la réponse
  def send(self, body, headers=[]):
     encoded = bytes(body, 'UTF-8') # encodage en UTF-8
     self.send_response(200)
     [self.send_header(*t) for t in headers]
     self.send_header('Content-Length',int(len(encoded)))
     self.end_headers()
     self.wfile.write(encoded)

  # On analyse la requête pour initialiser nos paramètres
  def init_params(self):
    # Analyse de l'adresse
    info = urlparse(self.path)
    self.path_info = [unquote(v) for v in info.path.split('/')[1:]]
    self.query_string = info.query
    self.params = parse_qs(info.query)

    # Récupération du corps
    length = self.headers.get('Content-Length')
    ctype = self.headers.get('Content-Type')
    if length:
      self.body = str(self.rfile.read(int(length)), 'utf-8')
      if ctype == 'application/x-www-form-urlencoded' : 
        self.params = parse_qs(self.body)
    else:
      self.body = ''
   
    # Traces
    # print('info_path =',self.path_info)
    # print('body =',length,ctype,self.body)
    # print('params =', self.params)


# Instanciation et lancement du serveur
httpd = socketserver.TCPServer(("", port), RequestHandler)
httpd.serve_forever()