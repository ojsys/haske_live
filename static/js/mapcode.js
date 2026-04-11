// initialize the map
var map = L.map('map', {
    center: [9.0820, 8.6753], // Centered on Nigeria
    zoom: 5, // Fixed zoom level
    zoomControl: true, // Disable zoom control
    dragging: true, // Disable dragging
    scrollWheelZoom: true, // Disable scroll wheel zoom
    doubleClickZoom: false, // Disable double click zoom
    boxZoom: false, // Disable box zoom
    keyboard: false // Disable keyboard navigation
});

var statesWithData = [];


// Update the hasData property based on the data source
geojsonData.features.forEach(function(feature){
if (statesWithData.includes(feature.properties.name)){
    feature.properties.hasData = true;
}
});

// Add GeoJSON layer to the map
L.geoJSON(geojsonData, {
    style: function(feature) {
        return {
            color: feature.properties.hasData ? 'green' : 'red',
            weight: 2,
            fillOpacity: 0.5
        };
    },
    onEachFeature: function(feature, layer) {
        // Add hover effect
        layer.on({
            // Show tooltip on mouseover
            mouseover: function(e) {
                var layer = e.target;
                layer.setStyle({
                    fillOpacity: 0.7
                });
                
                // Create and show tooltip
                layer.bindTooltip(feature.properties.name, {
                    permanent: false,
                    direction: 'center',
                    className: 'state-tooltip'
                }).openTooltip();
            },
            // Reset style on mouseout
            mouseout: function(e) {
                var layer = e.target;
                layer.setStyle({
                    fillOpacity: 0.5
                });
            },
            // Handle click event
            click: function(e) {
                var stateName = feature.properties.name;
                window.location.href = `http://localhost:8000/state/${stateName}`;
            }
        });
    }
}).addTo(map);