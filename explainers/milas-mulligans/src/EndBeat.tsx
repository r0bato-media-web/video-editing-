import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {brand, fonts, endUrl} from './brand';
import {clamp} from './common';
import {loadFont} from '@remotion/google-fonts/Inter';

// Load Inter with the render, so the card looks the same on a machine that doesn't have Inter installed.
loadFont('normal', {weights: ['600', '800'], subsets: ['latin']});

// 4.5 s payoff after a footage reel: the scholarship cap draws on, then the proceeds line, then the link.
// The proceeds line is the milasmulligans.com wording, used exactly (Rob, 21 Oct 2026). Never "every dollar".
// No "We play for Arian." here (Rob, 14 Oct 2026: not needed at the end).
const CAP = [
  'M200 90 L340 150 L200 210 L60 150 Z',
  'M120 180 V250 Q200 290 280 250 V180',
  'M200 150 L330 156 V236',
];

export const EndBeat: React.FC = () => {
  const f = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const v = height > width;
  const size = v ? 520 : 380;
  const per = 30 / CAP.length;
  const l1 = interpolate(f, [24, 34], [0, 1], clamp);
  const l3 = interpolate(f, [60, 70], [0, 1], clamp);
  // Vertical: the proceeds line is two lines (115 px) taller than the old one, so the cap's top margin is 115 px larger (-5, was -120). That keeps the cap exactly where it was.
  return (
    <AbsoluteFill style={{background: brand.paper, alignItems: 'center', justifyContent: 'center', flexDirection: 'column'}}>
      <svg viewBox="0 0 400 400" width={size} height={size} style={{marginTop: v ? -5 : -40}}>
        {CAP.map((d, i) => {
          const p = interpolate(f, [i * per, (i + 1) * per], [0, 1], clamp);
          return (
            <path key={i} d={d} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} opacity={p > 0 ? 1 : 0}
              fill="none" stroke={brand.ink} strokeWidth={8} strokeLinecap="round" strokeLinejoin="round" />
          );
        })}
      </svg>
      <div style={{fontFamily: fonts.sans, fontWeight: 600, fontSize: v ? 46 : 40, color: brand.ink, opacity: l1, textAlign: 'center', padding: '0 70px', lineHeight: 1.25, marginTop: v ? 10 : 0}}>
        Proceeds from the tournament
        <br />
        help fund the
        <br />
        <span style={{fontWeight: 800, color: brand.navy}}>Arian Walker Hannon-Kohler Memorial Scholarship</span>
        <br />
        and other charitable initiatives.
      </div>
      <div style={{fontFamily: fonts.sans, fontWeight: 800, fontSize: v ? 52 : 44, color: brand.white, background: brand.navy, padding: '14px 36px', borderRadius: 8, opacity: l3, marginTop: v ? 60 : 30}}>
        {endUrl}
      </div>
    </AbsoluteFill>
  );
};
