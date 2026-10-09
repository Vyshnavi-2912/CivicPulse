/* ==========================================================================
   CivicPulse Leaflet Map Module (Interactive Geographic Explorer)
   ========================================================================== */

let civicMap = null;
let mapMarkers = [];

function initCivicMap(containerId = 'mapContainer') {
    const mapElement = document.getElementById(containerId);
    if (!mapElement) return;

    // Center of India default coordinates
    const defaultCenter = [20.5937, 78.9629];
    const defaultZoom = 5;

    if (!civicMap) {
        civicMap = L.map(containerId).setView(defaultCenter, defaultZoom);

        // OpenStreetMap high-definition tile layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | CivicPulse SDG 11',
            maxZoom: 19
        }).addTo(civicMap);
    }

    // Pass current filter query parameters (URL search string) to API
    const currentParams = window.location.search || '';
    const apiUrl = '/api/reports' + currentParams;

    fetch(apiUrl)
        .then(res => res.json())
        .then(reports => {
            renderMapMarkers(reports);
            setTimeout(() => {
                if (civicMap) civicMap.invalidateSize();
            }, 300);
        })
        .catch(err => {
            console.error("Error fetching map reports:", err);
        });
}

function renderMapMarkers(reports) {
    if (!civicMap) return;

    // Clear existing markers
    mapMarkers.forEach(m => civicMap.removeLayer(m));
    mapMarkers = [];

    const bounds = [];

    reports.forEach(report => {
        if (report.latitude && report.longitude) {
            const lat = parseFloat(report.latitude);
            const lng = parseFloat(report.longitude);
            
            if (isNaN(lat) || isNaN(lng)) return;

            bounds.push([lat, lng]);

            // Custom pin color based on severity level
            let pinColor = '#2563EB'; // Low (Blue)
            let pinShadow = 'rgba(37, 99, 235, 0.4)';
            let iconSymbol = 'fa-circle-info';

            if (report.severity_level === 'Critical') {
                pinColor = '#DC2626'; // Critical (Red)
                pinShadow = 'rgba(220, 38, 38, 0.5)';
                iconSymbol = 'fa-triangle-exclamation';
            } else if (report.severity_level === 'High') {
                pinColor = '#EA580C'; // High (Orange)
                pinShadow = 'rgba(234, 88, 12, 0.45)';
                iconSymbol = 'fa-circle-exclamation';
            } else if (report.severity_level === 'Medium') {
                pinColor = '#D97706'; // Medium (Yellow)
                pinShadow = 'rgba(217, 119, 6, 0.4)';
                iconSymbol = 'fa-triangle-exclamation';
            }

            const customMarkerIcon = L.divIcon({
                className: 'custom-leaflet-pin',
                html: `
                    <div style="
                        background-color: ${pinColor};
                        width: 28px;
                        height: 28px;
                        border-radius: 50%;
                        border: 3px solid #FFFFFF;
                        box-shadow: 0 4px 10px ${pinShadow};
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: #FFFFFF;
                        font-size: 11px;
                    ">
                        <i class="fa-solid ${iconSymbol}"></i>
                    </div>
                `,
                iconSize: [28, 28],
                iconAnchor: [14, 14]
            });

            const marker = L.marker([lat, lng], { icon: customMarkerIcon }).addTo(civicMap);

            const sourceBadge = report.is_sample 
                ? `<span style="font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; background: #64748B; color: white;">Sample Demo</span>`
                : `<span style="font-size: 0.65rem; padding: 2px 6px; border-radius: 4px; background: #0D9488; color: white;">Real Submission</span>`;

            const popupContent = `
                <div style="max-width: 250px; font-family: 'Inter', system-ui, sans-serif; padding: 2px;">
                    <div style="width: 100%; height: 130px; border-radius: 8px; overflow: hidden; background-color: #0F172A; margin-bottom: 8px; border: 1px solid #E2E8F0;">
                        <img src="${report.image_path}" 
                             style="width: 100%; height: 100%; object-fit: cover;" 
                             alt="${report.category}"
                             onerror="this.onerror=null; this.src='data:image/svg+xml;utf8,<svg xmlns=\\'http://www.w3.org/2000/svg\\' width=\\'250\\' height=\\'130\\' viewBox=\\'0 0 250 130\\'><rect width=\\'250\\' height=\\'130\\' fill=\\'%230F172A\\'/><text x=\\'50%\\' y=\\'50%\\' fill=\\'%2394A3B8\\' font-family=\\'sans-serif\\' font-size=\\'14\\' text-anchor=\\'middle\\' dominant-baseline=\\'middle\\'>CivicPulse Report Image</text></svg>';">
                    </div>
                    <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px;">
                        <span style="font-size: 0.72rem; font-weight: 800; color: #64748B;">${report.id}</span>
                        ${sourceBadge}
                    </div>
                    <div style="font-size: 0.98rem; font-weight: 800; color: #0F172A; margin-bottom: 4px; line-height: 1.2;">${report.category}</div>
                    <div style="font-size: 0.82rem; color: #475569; margin-bottom: 8px; line-height: 1.3;">
                        <i class="fa-solid fa-location-dot" style="color: #0D9488;"></i> ${report.village_city}, ${report.district}
                    </div>
                    <div style="display: flex; gap: 6px; margin-bottom: 10px; flex-wrap: wrap;">
                        <span style="font-size: 0.68rem; font-weight: 700; padding: 3px 7px; border-radius: 4px; background: ${pinColor}; color: white;">SEVERITY: ${report.severity_level.toUpperCase()}</span>
                        <span style="font-size: 0.68rem; font-weight: 700; padding: 3px 7px; border-radius: 4px; background: #1E293B; color: white;">STATUS: ${report.status}</span>
                    </div>
                    <a href="/report/${report.id}" style="display: block; text-align: center; background: #0D9488; color: #FFFFFF; text-decoration: none; padding: 8px 12px; border-radius: 6px; font-weight: 700; font-size: 0.85rem; transition: background 0.2s;">
                        View Full Details <i class="fa-solid fa-arrow-right" style="font-size: 0.75rem; margin-left: 4px;"></i>
                    </a>
                </div>
            `;

            marker.bindPopup(popupContent);
            mapMarkers.push(marker);
        }
    });

    if (bounds.length > 0) {
        if (bounds.length === 1) {
            civicMap.setView(bounds[0], 11);
        } else {
            civicMap.fitBounds(bounds, { padding: [40, 40], maxZoom: 13 });
        }
    } else {
        // Fallback view if no markers match
        civicMap.setView([20.5937, 78.9629], 5);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initCivicMap('mapContainer');

    window.addEventListener('resize', function() {
        if (civicMap) civicMap.invalidateSize();
    });
});
