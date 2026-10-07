import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {brand, fonts, endText, endUrl} from './brand';
import {clamp} from './common';

// 4.5 s payoff after a footage reel: the scholarship cap draws on, then the line, then the link.
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
  const l2 = interpolate(f, [60, 70], [0, 1], clamp);
  const l3 = interpolate(f, [78, 88], [0, 1], clamp);
  return (
    <AbsoluteFill style={{background: brand.paper, alignItems: 'center', justifyContent: 'center', flexDirection: 'column'}}>
      <svg viewBox="0 0 400 400" width={size} height={size} style={{marginTop: v ? -120 : -40}}>
        {CAP.map((d, i) => {
          const p = interpolate(f, [i * per, (i + 1) * per], [0, 1], clamp);
          return (
            <path key={i} d={d} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - p} opacity={p > 0 ? 1 : 0}
              fill="none" stroke={brand.ink} strokeWidth={8} strokeLinecap="round" strokeLinejoin="round" />
          );
        })}
      </svg>
      <div style={{fontFamily: fonts.sans, fontWeight: 600, fontSize: v ? 46 : 40, color: brand.ink, opacity: l1, textAlign: 'center', padding: '0 70px', lineHeight: 1.25, marginTop: v ? 10 : 0}}>
        Every dollar goes to the
        <br />
        <span style={{fontWeight: 800, color: brand.navy}}>Arian Walker Hannon-Kohler Memorial Scholarship</span>
      </div>
      <div style={{fontFamily: fonts.serif, fontSize: v ? 96 : 76, color: brand.navy, opacity: l2, marginTop: v ? 50 : 24}}>{endText}</div>
      <div style={{fontFamily: fonts.sans, fontWeight: 800, fontSize: v ? 52 : 44, color: brand.white, background: brand.navy, padding: '14px 36px', borderRadius: 8, opacity: l3, marginTop: v ? 30 : 18}}>
        {endUrl}
      </div>
    </AbsoluteFill>
  );
};
