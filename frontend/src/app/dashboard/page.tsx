'use client';

import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Building2, MapPin, Tags } from 'lucide-react';
import { PageContainer, PageHeader } from '@/components/PageContainer';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/Card';
import { Alert } from '@/components/Alert';
import { categoryAPI, civicAPI } from '@/lib/api';
import { useLocalizedField } from '@/hooks/useLocalizedField';
import type { Category, IdeaHotspotResponse, IdeaMapItem } from '@/types';

const WORLD_BOUNDS = {
  min_lat: -90,
  min_lng: -180,
  max_lat: 90,
  max_lng: 180,
};

interface CategoryDatum {
  name: string;
  count: number;
}

export default function CivicDashboardPage() {
  const { t } = useTranslation();
  const { getCategoryName } = useLocalizedField();

  const [hotspots, setHotspots] = useState<IdeaHotspotResponse | null>(null);
  const [items, setItems] = useState<IdeaMapItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let active = true;

    setIsLoading(true);
    setError('');

    Promise.all([
      civicAPI.getHotspots(20),
      civicAPI.getMap(WORLD_BOUNDS),
      categoryAPI.getAll(),
    ])
      .then(([hotspotData, mapItems, categoryData]) => {
        if (!active) return;
        setHotspots(hotspotData);
        setItems(mapItems);
        setCategories(categoryData);
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

  const categoryData = useMemo<CategoryDatum[]>(() => {
    const counts = new Map<number, number>();
    for (const item of items) {
      counts.set(item.category_id, (counts.get(item.category_id) || 0) + 1);
    }

    const nameById = new Map(categories.map((category) => [category.id, getCategoryName(category)]));

    return Array.from(counts.entries())
      .map(([categoryId, count]) => ({
        name: nameById.get(categoryId) || String(categoryId),
        count,
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8);
  }, [items, categories, getCategoryName]);

  const topNeighborhoods = hotspots?.neighborhoods.slice(0, 10) ?? [];

  const stats = [
    {
      key: 'totalPinned',
      label: t('civic.dashboard.totalPinned'),
      value: hotspots?.total ?? 0,
      icon: <MapPin className="w-5 h-5" />,
    },
    {
      key: 'totalNeighborhoods',
      label: t('civic.dashboard.totalNeighborhoods'),
      value: hotspots?.neighborhoods.length ?? 0,
      icon: <Building2 className="w-5 h-5" />,
    },
    {
      key: 'topCategories',
      label: t('civic.dashboard.topIssues'),
      value: categoryData.length,
      icon: <Tags className="w-5 h-5" />,
    },
  ];

  return (
    <PageContainer maxWidth="7xl" paddingY="loose">
      <PageHeader
        title={t('civic.dashboard.title')}
        description={t('civic.dashboard.description')}
      />

      {error && (
        <div className="mb-6">
          <Alert variant="error">{error}</Alert>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
        {stats.map((stat) => (
          <Card key={stat.key}>
            <div className="flex items-center justify-between mb-3 text-gray-500 dark:text-gray-400">
              <span className="text-sm font-medium">{stat.label}</span>
              {stat.icon}
            </div>
            <p className="text-3xl font-semibold text-gray-900 dark:text-gray-100">
              {isLoading ? '—' : stat.value}
            </p>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>{t('civic.dashboard.topIssues')}</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-[320px] w-full bg-gray-100 dark:bg-gray-800 rounded animate-pulse" />
            ) : categoryData.length === 0 ? (
              <p className="h-[320px] flex items-center justify-center text-sm text-gray-500 dark:text-gray-400">
                {t('civic.dashboard.noData')}
              </p>
            ) : (
              <div className="h-[320px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={categoryData} layout="vertical" margin={{ left: 8, right: 16 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="currentColor" className="text-gray-200 dark:text-gray-700" horizontal={false} />
                    <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} />
                    <YAxis
                      type="category"
                      dataKey="name"
                      width={120}
                      tick={{ fontSize: 12 }}
                    />
                    <Tooltip
                      cursor={{ fill: 'rgba(31, 111, 92, 0.08)' }}
                      contentStyle={{
                        borderRadius: 8,
                        border: '1px solid #E2E0D8',
                        fontSize: 12,
                      }}
                    />
                    <Bar dataKey="count" fill="#1F6F5C" radius={[0, 6, 6, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t('civic.dashboard.topNeighborhoods')}</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                {Array.from({ length: 5 }).map((_, index) => (
                  <div
                    key={index}
                    className="h-10 w-full bg-gray-100 dark:bg-gray-800 rounded animate-pulse"
                  />
                ))}
              </div>
            ) : topNeighborhoods.length === 0 ? (
              <p className="h-[320px] flex items-center justify-center text-sm text-gray-500 dark:text-gray-400">
                {t('civic.dashboard.noData')}
              </p>
            ) : (
              <ul className="divide-y divide-gray-100 dark:divide-gray-700">
                {topNeighborhoods.map((hotspot) => (
                  <li
                    key={`${hotspot.neighborhood}-${hotspot.latitude}-${hotspot.longitude}`}
                    className="flex items-center justify-between py-3"
                  >
                    <span className="text-sm font-medium text-gray-800 dark:text-gray-200">
                      {hotspot.neighborhood}
                    </span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                      {t('civic.dashboard.ideasCount', { count: hotspot.count })}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </PageContainer>
  );
}
