from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtCore import QTimer

class MapWidget(QWidget):
    def __init__(self, vehicle=None):
        super().__init__()
        self.vehicle = vehicle

        self.default_lat = 37.5665  
        self.default_lon = 126.9780
        self.default_heading = 0

        self.view = QWebEngineView()
        layout = QVBoxLayout(self)
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)

        self.update_map()

        self.view.loadFinished.connect(self.start_update_position)

    def update_map(self):
        lat, lon, heading = self.get_gps_info()

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        html, body {{
            height: 100%;
            margin: 0;
            padding: 0;
            overflow: hidden;
        }}
        #mapid {{
            width: 100%;
            height: 100%;  
            background: rgba(255, 255, 255, 0);
        }}
    </style>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
</head>
<body>
    <div id="mapid"></div>

    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            var map = L.map('mapid', {{ zoomControl: false }}).setView([{lat}, {lon}], 18);

            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 19,
            }}).addTo(map);

            var customIcon = L.divIcon({{
                html: '<img src="https://i.postimg.cc/k424HYgn/icon.png" id="drone-icon" style="width: 40px; height: 40px;" />',
                className: '',
                iconSize: [40, 40],  
                iconAnchor: [20, 20]  
            }});

            var marker = L.marker([{lat}, {lon}], {{ icon: customIcon }}).addTo(map);

            window.updateMarker = function(lat, lon, heading) {{
                marker.setLatLng([lat, lon]);
                map.setView([lat, lon], map.getZoom());
                var iconElement = document.getElementById("drone-icon");
                iconElement.style.transform = "rotate(" + heading + "deg)"; 
            }}
        }});
    </script>
</body>
</html>
"""

        self.view.setHtml(html_content)


    def get_gps_info(self):
        if self.vehicle:
            location = self.vehicle.location.global_frame
            heading = self.vehicle.heading
            lat = location.lat
            lon = location.lon
        else:
            lat, lon, heading = self.default_lat, self.default_lon, self.default_heading
        return lat, lon, heading

    def start_update_position(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(10)

    def update_position(self):
        lat, lon, heading = self.get_gps_info()
        self.view.page().runJavaScript(f"updateMarker({lat}, {lon}, {heading});")

    def update_vehicle(self, vehicle):
        self.vehicle = vehicle
