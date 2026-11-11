import { ImageResponse } from 'next/og';

export const runtime = 'edge';

// Read from environment (could also fetch from API)
const instanceName = process.env.NEXT_PUBLIC_INSTANCE_NAME || 'Bengaluru Civic Suggestion Box';

export const alt = instanceName;
export const size = {
  width: 1200,
  height: 630,
};
export const contentType = 'image/png';

export default async function OGImage() {
  const tagline = process.env.NEXT_PUBLIC_TAGLINE || 'Share your ideas to improve Bengaluru';
  const primaryColor = process.env.NEXT_PUBLIC_PRIMARY_COLOR || '#1F6F5C';
  const secondaryColor = process.env.NEXT_PUBLIC_SECONDARY_COLOR || '#121A17';

  return new ImageResponse(
    <div
      style={{
        background: `linear-gradient(135deg, ${primaryColor} 0%, ${secondaryColor} 100%)`,
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 60,
      }}
    >
      <div
        style={{
          fontSize: 72,
          fontWeight: 'bold',
          color: 'white',
          marginBottom: 24,
        }}
      >
        {instanceName}
      </div>
      <div
        style={{
          fontSize: 36,
          color: 'rgba(255,255,255,0.9)',
          textAlign: 'center',
        }}
      >
        {tagline}
      </div>
    </div>,
    {
      ...size,
    }
  );
}
