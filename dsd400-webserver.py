#!/usr/bin/env python3
#
# Exempel för DSD400-kursen. Webbserver som tillhandahåller statiska
# filer från "html"-katalogen samt genererad dynamiskt JSON för
# URL:er som börjar på "/api".
#
# Thomas Lundqvist, 2020, use freely!

from http.server import SimpleHTTPRequestHandler, HTTPServer
import json, random
import pymysql.cursors
import pprint
import mimetypes


INTERFACES = '192.168.1.99'
PORT = 8020

# This class will handle any incoming GET requests
# URLs starting with /api/ is catched for REST/JSON calls
# Other URLs are handled by default handler to serve static
# content (directories, files)

class RequestHandler(SimpleHTTPRequestHandler):
        

    # Override handler for GET requests
    def do_GET(self):
        
        if self.path.startswith('/api'):
            self.send_response(200)
            self.send_header('Content-type','text/json')
            self.end_headers()

        
                
                
            if self.path.startswith("/api/getprisoner"):
                connection = pymysql.connect(host='dsd400.port0.org',
                             user='pyJAFKD',
                             password='lurigtlösen'.encode().decode('latin1'),
                             database='JFPrisonerDB',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

                with connection:
                    with connection.cursor() as cursor:
                        # Read records
                        cursor.execute("SELECT * FROM Perputrator")
                        result = cursor.fetchall()
                        
                response = result
            else:
                response = {'error': 'Not implemented'}
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Call default serving static files if not '/api'
        # from 'html' subdirectory
        self.path = '/html' + self.path
        return super().do_GET()
    
    def do_POST(self):
        if self.path.startswith("/api/save_data"):
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))

            # Print the data received from the client
            print("Received data:", data)

            # Now you can access the values using data["birthID"], data["name"], data["age"], and data["gender"]
            # Process the data as needed

            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()
            response = {"status": "success"}
            self.wfile.write(json.dumps(response).encode())
            
            connection = pymysql.connect(host='dsd400.port0.org',
                             user='pyJAFKD',
                             password='lurigtlösen'.encode().decode('latin1'),
                             database='JFPrisonerDB',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

            with connection:
                with connection.cursor() as cursor:
                    # Read records
                    
                    sql = "INSERT INTO Perputrator VALUES(%s, %s, %s, %s)"
                    val = (data["birthID"], data["name"], data["age"], data["gender"])
                    
                    cursor.execute(sql, val)
                    connection.commit()

                # Send the response dict as json message
                response = {'text': 'Prisoner registred successfully.'}
            
            return

        # Return an error for other POST paths
        self.send_response(400)
        self.end_headers()
        response = {"error": "Not implemented"}
        self.wfile.write(json.dumps(response).encode())
        return
    
try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer((INTERFACES, PORT), RequestHandler)
    print('Starting HTTP server on http://' + INTERFACES + ":" + str(PORT))
    server.serve_forever()
    
except KeyboardInterrupt:
    print('Ctrl-C received, shutting down the web server')
    server.socket.close()

