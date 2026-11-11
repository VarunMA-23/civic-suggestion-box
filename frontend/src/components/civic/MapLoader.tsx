'use client';

import dynamic from 'next/dynamic';

const MapSkeleton = ({ height }: { height: number }) => (
  <div
    className="w-full rounded-xl bg-gray-100 dark:bg-gray-800 animate-pulse border border-gray-200 dark:border-gray-700"
    style={{ height }}
  />
);

export const MapPicker = dynamic(
  () => import('./MapPicker').then((module) => module.MapPicker),
  {
    ssr: false,
    loading: () => <MapSkeleton height={320} />,
  }
);

export const LiveMap = dynamic(
  () => import('./LiveMap').then((module) => module.LiveMap),
  {
    ssr: false,
    loading: () => <MapSkeleton height={560} />,
  }
);
