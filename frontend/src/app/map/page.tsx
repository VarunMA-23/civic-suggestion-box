'use client';

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { MapPin } from 'lucide-react';
import { PageContainer, PageHeader } from '@/components/PageContainer';
import { Card } from '@/components/Card';
import { Alert } from '@/components/Alert';
import { LiveMap } from '@/components/civic/MapLoader';
import { civicAPI } from '@/lib/api';
import type { IdeaMapItem } from '@/types';

const WORLD_BOUNDS = {
  min_lat: -90,
  min_lng: -180,
  max_lat: 90,
  max_lng: 180,
};

export default function CivicMapPage() {
  const { t } = useTranslation();
  const [items, setItems] = useState<IdeaMapItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    setIsLoading(true);
    setError('');

    civicAPI
      .getMap(WORLD_BOUNDS)
      .then((data) => {
        if (active) setItems(data);
      })
      .catch(() => {
        if (active) setError(t('common.error'));
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [t]);

  return (
    <PageContainer maxWidth="7xl" paddingY="loose">
      <PageHeader
        title={t('civic.map.title')}
        description={t('civic.map.description')}
      />

      {error && (
        <div className="mb-6">
          <Alert variant="error">{error}</Alert>
        </div>
      )}

      <Card className="p-0 overflow-hidden">
        {isLoading ? (
          <div className="h-[560px] w-full bg-gray-100 dark:bg-gray-800 animate-pulse" />
        ) : items.length === 0 ? (
          <div className="h-[560px] w-full flex flex-col items-center justify-center gap-3 text-gray-500 dark:text-gray-400">
            <MapPin className="w-10 h-10" />
            <p className="text-sm">{t('civic.map.noIdeas')}</p>
          </div>
        ) : (
          <LiveMap items={items} height={560} className="border-0 rounded-none" />
        )}
      </Card>

      {!isLoading && items.length > 0 && (
        <p className="mt-4 text-sm text-gray-500 dark:text-gray-400">
          {t('civic.dashboard.ideasCount', { count: items.length })}
        </p>
      )}
    </PageContainer>
  );
}
