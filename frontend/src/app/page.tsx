import type { Metadata } from 'next';
import { getBaseMetadata, getSiteConfig } from '@/lib/seo/metadata';
import { generateCollectionPageSchema } from '@/lib/seo/structured-data';
import { StructuredData } from '@/components/seo/StructuredData';
import HomePageClient from '@/components/pages/HomePageClient';

// Force static generation - data is fetched client-side anyway
// This enables Cloudflare to cache the page HTML
export const dynamic = 'force-static';

// Allow revalidation every hour for SEO metadata updates
export const revalidate = 3600;

// Metadata is generated at build time, use environment fallbacks
export function generateMetadata(): Metadata {
  const instanceName = process.env.NEXT_PUBLIC_INSTANCE_NAME || 'Bengaluru Civic Suggestion Box';
  const tagline = process.env.NEXT_PUBLIC_TAGLINE || 'Citizen platform for ideas and community initiatives';

  return {
    ...getBaseMetadata('en'),
    title: instanceName,
    description: tagline,
    openGraph: {
      title: instanceName,
      description: tagline,
    },
  };
}

// Get site config for structured data
const siteConfig = getSiteConfig();

const collectionSchema = generateCollectionPageSchema(
  siteConfig.name.en ?? 'Bengaluru Civic Suggestion Box',
  siteConfig.description.en ?? 'Citizen platform for ideas',
  siteConfig.url,
  100,
  'en'
);

export default function HomePage() {
  return (
    <>
      <StructuredData data={collectionSchema} />
      <HomePageClient />
    </>
  );
}
