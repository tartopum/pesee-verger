from microdot import Microdot

app = Microdot()

@app.route('/')
def index(request):
    return "<h1>Serveur Pico W Multi-WiFi</h1><p>Tout fonctionne !</p>", {'Content-Type': 'text/html'}