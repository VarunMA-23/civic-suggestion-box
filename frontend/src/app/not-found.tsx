import type { Metadata } from 'next';
import { NotFoundContent } from '@/components/NotFoundContent';

export const metadata: Metadata = {
  title: 'Page Not Found | Bengaluru Civic Suggestion Box',
  description: 'The page you are looking for does not exist or has been moved.',
  robots: {
    index: false,
    follow: true,
  },
};

export default function NotFound() {
  return <NotFoundContent />;
}
