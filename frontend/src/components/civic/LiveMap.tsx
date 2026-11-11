'use client';

import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import Link from 'next/link';
import L from 'leaflet';
import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import type { IdeaMapItem } from '@/types';
import { usePlatformConfig } from '@/lib/config/PlatformConfigProvider';

export interface LiveMapProps {
  items: IdeaMapItem[];
  height?: number;
  className?: string;
}

const DEFAULT_CENTER: [number, number] = [20, 0];

const pinIcon = L.divIcon({
  className: '',
  html: '<div style="width:20px;height:20px;border-radius:9999px;background:#1F6F5C;border:3px solid #ffffff;box-shadow:0 2px 6px rgba(0,0,0,0.35)"></div>',
  iconSize: [20, 20],
  iconAnchor: [10, 10],
});

function FitBounds({ items }: { items: IdeaMapItem[] }) {
  const map = useMap();

  useEffect(() => {
    if (items.length === 0) return;
    const bounds = L.latLngBounds(items.map((item) => [item.latitude, item.longitude]));
    if (bounds.isValid()) {
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 15 });
    }
  }, [map, items]);

  return null;
}

export function LiveMap({ items, height = 560, className = '' }: LiveMapProps) {
  const { t } = useTranslation();
  const { config } = usePlatformConfig();

  const center = useMemo<[number, number]>(() => {
    if (items.length > 0) {
      return [items[0].latitude, items[0].longitude];
    }
    const coords = config?.instance?.location?.coordinates;
    if (coords && (coords.lat !== 0 || coords.lng !== 0)) {
      return [coords.lat, coords.lng];
    }
    return DEFAULT_CENTER;
  }, [items, config]);

  return (
    <div
      className={`w-full rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700 ${className}`}
      style={{ height }}
    >
      <MapContainer
        center={center}
        zoom={items.length > 0 ? 12 : 3}
        scrollWheelZoom
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        <FitBounds items={items} />
        {items.map((item) => (
          <Marker key={item.id} position={[item.latitude, item.longitude]} icon={pinIcon}>
            <Popup>
              <div className="space-y-1 min-w-[180px]">
                <p className="font-semibold text-gray-900">{item.title}</p>
                {item.neighborhood && (
                  <p className="text-xs text-gray-600">{item.neighborhood}</p>
                )}
                <p className="text-xs text-gray-600">
                  {item.upvotes} ↑ / {item.downvotes} ↓ · {item.score}
                </p>
                <Link
                  href={`/ideas/${item.id}`}
                  className="text-xs font-medium text-primary-600 hover:text-primary-700"
                >
                  {t('civic.map.viewIdea')}
                </Link>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}

export default LiveMap;
