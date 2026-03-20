import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useNavigate } from 'react-router-dom';

export default function CityMap({ junctions }) {
  const navigate = useNavigate();

  // Compute default center
  let center = [20.5937, 78.9629];
  if (junctions && junctions.length > 0) {
    const avgLat = junctions.reduce((sum, j) => sum + j.lat, 0) / junctions.length;
    const avgLng = junctions.reduce((sum, j) => sum + j.lng, 0) / junctions.length;
    center = [avgLat, avgLng];
  }

  if (!junctions || junctions.length === 0) {
    return (
      <div className="w-full h-full bg-transparent flex flex-col items-center justify-center font-mono text-[var(--accent)] gap-4">
        <div className="w-16 h-16 relative">
          <div className="absolute inset-0 border-2 border-[var(--accent)] border-t-transparent rounded-full animate-spin"></div>
          <div className="absolute inset-2 border-2 border-[var(--border-glow)] border-b-transparent rounded-full animate-spin" style={{animationDirection: 'reverse', animationDuration: '1.5s'}}></div>
        </div>
        <div className="tracking-[0.2em] font-bold text-sm hover-glitch">AWAITING SATELLITE TELEMETRY</div>
      </div>
    );
  }

  const getCongestionColor = (congestion) => {
    if (congestion === 'heavy') return '#ef4444'; // var(--danger)
    if (congestion === 'moderate') return '#f59e0b'; // var(--warning)
    return '#10b981'; // var(--success) clear or undefined
  };

  return (
    <div className="w-full h-full bg-transparent">
      <MapContainer 
        center={center} 
        zoom={12} 
        style={{ width: '100%', height: '100%', background: 'transparent' }}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution="&copy; <a href='https://carto.com/'>CartoDB</a>"
        />
        {junctions.map(j => (
          <CircleMarker
            key={j.id}
            center={[j.lat, j.lng]}
            radius={window.innerWidth > 1024 ? 10 : 8}
            color={getCongestionColor(j.congestion)}
            fillColor={getCongestionColor(j.congestion)}
            fillOpacity={0.8}
            weight={2}
            className="animate-pulse"
            eventHandlers={{
              click: () => navigate(`/junction/${j.id}`)
            }}
          >
            <Popup className="custom-popup">
              <div className="bg-[var(--surface-solid)] border border-[var(--border)] p-3 rounded-lg shadow-[0_0_20px_rgba(0,0,0,0.8)] -m-3 min-w-[200px]">
                <div className="font-rajdhani uppercase font-bold text-lg text-white tracking-widest border-b border-[var(--border)] pb-1 mb-2">
                  {j.name}
                </div>
                <div className="flex justify-between items-center mb-1">
                  <span className="font-mono text-[var(--muted)] text-[10px] uppercase">Zone</span>
                  <span className="font-mono text-white text-xs font-bold">{j.city}</span>
                </div>
                <div className="flex justify-between items-center mb-2">
                  <span className="font-mono text-[var(--muted)] text-[10px] uppercase">Traffic</span>
                  <span 
                    className="font-mono text-[10px] uppercase font-bold px-1.5 py-0.5 rounded"
                    style={{ backgroundColor: `${getCongestionColor(j.congestion)}33`, color: getCongestionColor(j.congestion) }}
                  >
                    {j.congestion || 'CLEAR'}
                  </span>
                </div>
                <div className="mt-3 text-center">
                  <span className="text-[10px] text-[var(--accent)] uppercase hover:text-white transition-colors cursor-pointer border-b border-transparent hover:border-[var(--accent)] pb-0.5">
                    View Camera Feed &rarr;
                  </span>
                </div>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
      <style>{`
        .leaflet-popup-content-wrapper, .leaflet-popup-tip {
          background: transparent !important;
          box-shadow: none !important;
        }
        .leaflet-popup-content { margin: 0; }
        .leaflet-container a.leaflet-popup-close-button {
          color: var(--muted);
          top: 6px;
          right: 6px;
          z-index: 10;
        }
        .leaflet-container a.leaflet-popup-close-button:hover {
          color: white;
        }
      `}</style>
    </div>
  );
}
