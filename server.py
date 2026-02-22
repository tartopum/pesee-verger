from microdot import Microdot, send_file

from io import read_pressure_voltage

app = Microdot()

@app.route("/")
def index(request):
    return send_file("templates/index.html")


@app.route("/api/pressure-voltage/")
def pressure_voltage(request):
    return {"pressure_voltage": read_pressure_voltage()}