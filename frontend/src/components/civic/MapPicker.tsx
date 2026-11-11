'use client';

import { useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import L from 'leaflet';
import { MapContainer, Marker, TileLayer, useMap, useMapEvents } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Input } from '@/components/Input';
import { usePlatformConfig } from '@/lib/config/PlatformConfigProvider';

export interface MapPoint {
  latitude: number;
  longitude: number;
}

export interface MapPickerProps {
  value: MapPoint | null;
  onChange: (value: MapPoint) => void;
  neighborhood: string;
  onNeighborhoodChange: (value: string) => void;
  address: string;
  onAddressChange: (value: string) => void;
  height?: number;
}

const DEFAULT_CENTER: [number, number] = [20, 0];

const pinIcon = L.divIcon({
  className: '',
  html: '<div style="width:22px;height:22px;border-radius:9999px;background:#1F6F5C;border:3px solid #ffffff;box-shadow:0 2px 6px rgba(0,0,0,0.35)"></div>',
  iconSize: [22, 22],
  iconAnchor: [11, 11],
});

function ClickHandler({ onChange }: { onChange: (value: MapPoint) => void }) {
  useMapEvents({
    click(event) {
      onChange({
        latitude: Number(event.latlng.lat.toFixed(6)),
        longitude: Number(event.latlng.lng.toFixed(6)),
      });
    },
  });
  return null;
}

function Recenter({ point }: { point: MapPoint | null }) {
  const map = useMap();

  useEffect(() => {
    if (point) {
      map.setView([point.latitude, point.longitude], Math.max(map.getZoom(), 14), {
        animate: true,
      });
    }
  }, [map, point]);

  return null;
}

export function MapPicker({
  value,
  onChange,
  neighborhood,
  onNeighborhoodChange,
  address,
  onAddressChange,
  height = 320,
}: MapPickerProps) {
  const { t } = useTranslation();
  const { config } = usePlatformConfig();

  const center = useMemo<[number, number]>(() => {
    const coords = config?.instance?.location?.coordinates;
    if (coords && (coords.lat !== 0 || coords.lng !== 0)) {
      return [coords.lat, coords.lng];
    }
    return DEFAULT_CENTER;
  }, [config]);

  return (
    <div className="space-y-4">
      <p className="text-sm text-gray-600 dark:text-gray-400">{t('civic.location.pickOnMap')}</p>

      <div
        className="w-full rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700"
        style={{ height }}
      >
        <MapContainer
          center={center}
          zoom={value ? 15 : 3}
          scrollWheelZoom
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          />
          <ClickHandler onChange={onChange} />
          <Recenter point={value} />
          {value && (
            <Marker
              position={[value.latitude, value.longitude]}
              icon={pinIcon}
              draggable
              eventHandlers={{
                dragend(event) {
                  const latlng = (event.target as L.Marker).getLatLng();
                  onChange({
                    latitude: Number(latlng.lat.toFixed(6)),
                    longitude: Number(latlng.lng.toFixed(6)),
                  });
                },
              }}
            />
          )}
        </MapContainer>
      </div>

      {value && (
        <p className="text-xs text-gray-500 dark:text-gray-400">
          {t('civic.location.latitude')}: {value.latitude}, {t('civic.location.longitude')}:{' '}
          {value.longitude}
        </p>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Input
          label={t('civic.location.neighborhood')}
          value={neighborhood}
          onChange={(e) => onNeighborhoodChange(e.target.value)}
          placeholder={t('civic.location.neighborhoodPlaceholder')}
          maxLength={150}
        />
        <Input
          label={t('civic.location.address')}
          value={address}
          onChange={(e) => onAddressChange(e.target.value)}
          placeholder={t('civic.location.addressPlaceholder')}
          maxLength={500}
        />
      </div>
    </div>
  );
}

export default MapPicker;
