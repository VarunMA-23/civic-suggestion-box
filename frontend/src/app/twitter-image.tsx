import { ImageResponse } from 'next/og';

export const runtime = 'edge';

export const alt = 'Bengaluru Civic Suggestion Box';
export const size = {
  width: 1200,
  height: 600,
};
export const contentType = 'image/png';

export default async function TwitterImage() {
  return new ImageResponse(
    <div
      style={{
        background: 'linear-gradient(135deg, #1F6F5C 0%, #121A17 100%)',
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 50,
      }}
    >
      <div
        style={{
          fontSize: 64,
          fontWeight: 'bold',
          color: 'white',
          marginBottom: 16,
        }}
      >
        Bengaluru Civic Suggestion Box
      </div>
      <div
        style={{
          fontSize: 28,
          color: 'rgba(255,255,255,0.9)',
          textAlign: 'center',
        }}
      >
        Citizen platform to improve Bengaluru
      </div>
    </div>,
    {
      ...size,
    }
  );
}
