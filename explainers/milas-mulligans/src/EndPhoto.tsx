import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {brand, fonts, endUrl} from './brand';
import {clamp} from './common';
import {loadFont} from '@remotion/google-fonts/Inter';

loadFont('normal', {weights: ['800'], subsets: ['latin']});

// 3 s ending for the 2025 throwback reels (Rob, 16 Nov 2026: the white card was too long and too plain, "should have a picture").
// A real 2025 tournament photo, darkened, with the client's logo (scaled and placed only, never redrawn) and the link.
// No proceeds sentence here: it stays in the caption (Rob's pick, 16 Nov 2026).
// logoW and top place the logo per photo, so it never sits on a person (dx shifts the block sideways, linkSize sizes the link): top = 0 centres the block, any other value is its distance from the top edge.
export const EndPhoto: React.FC<{photo: string; dim: number; logoW?: number; top?: number; dx?: number; linkSize?: number}> = ({photo, dim, logoW = 700, top = 0, dx = 0, linkSize = 56}) => {
  const f = useCurrentFrame();
  const zoom = interpolate(f, [0, 90], [1, 1.05], clamp);
  const logo = interpolate(f, [8, 18], [0, 1], clamp);
  const logoY = interpolate(f, [8, 18], [24, 0], clamp);
  const link = interpolate(f, [20, 30], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <AbsoluteFill style={{transform: `scale(${zoom})`}}>
        <Img src={staticFile(photo)} style={{width: '100%', height: '100%', objectFit: 'cover'}} />
      </AbsoluteFill>
      <AbsoluteFill style={{background: `rgba(6, 18, 40, ${dim})`}} />
      <AbsoluteFill style={{alignItems: 'center', justifyContent: top ? 'flex-start' : 'center', paddingTop: top, flexDirection: 'column', transform: `translateX(${dx}px)`}}>
        <Img src={staticFile('logo.png')} style={{width: logoW, opacity: logo, transform: `translateY(${logoY}px)`}} />
        <div style={{fontFamily: fonts.sans, fontWeight: 800, fontSize: linkSize, color: brand.navy, background: brand.white, padding: '16px 40px', borderRadius: 8, opacity: link, marginTop: top ? 44 : 70}}>
          {endUrl}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
