import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {brand, fonts, titleText, endText, endUrl} from './brand';

export const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Scales type to the frame so labels stay readable on a phone in both shapes.
export const useType = () => {
  const {width, height} = useVideoConfig();
  const vertical = height > width;
  return {
    vertical,
    title: vertical ? 92 : 84,
    label: vertical ? 64 : 64,
    sub: vertical ? 50 : 52,
  };
};

export const TitleCard: React.FC = () => {
  const f = useCurrentFrame();
  const t = useType();
  const o = interpolate(f, [0, 12], [0, 1], clamp);
  const y = interpolate(f, [0, 12], [24, 0], clamp);
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', padding: 80}}>
      <div
        style={{
          fontFamily: fonts.serif,
          fontSize: t.title * 1.25,
          color: brand.navy,
          textAlign: 'center',
          lineHeight: 1.1,
          opacity: o,
          transform: `translateY(${y}px)`,
          maxWidth: t.vertical ? 900 : 1500,
        }}
      >
        {titleText}
      </div>
    </AbsoluteFill>
  );
};

export const EndCard: React.FC = () => {
  const f = useCurrentFrame();
  const t = useType();
  const o1 = interpolate(f, [0, 12], [0, 1], clamp);
  const o2 = interpolate(f, [10, 22], [0, 1], clamp);
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', gap: 36, flexDirection: 'column'}}>
      <div style={{fontFamily: fonts.serif, fontSize: t.title * 1.2, color: brand.navy, opacity: o1}}>{endText}</div>
      <div
        style={{
          fontFamily: fonts.sans,
          fontWeight: 800,
          fontSize: t.label,
          color: brand.white,
          background: brand.navy,
          padding: '18px 40px',
          borderRadius: 8,
          opacity: o2,
        }}
      >
        {endUrl}
      </div>
    </AbsoluteFill>
  );
};

// Lower band that carries the active step's detail line.
export const SubBand: React.FC<{text: string; start: number}> = ({text, start}) => {
  const f = useCurrentFrame();
  const t = useType();
  const o = interpolate(f, [start, start + 10], [0, 1], clamp);
  return (
    <div
      style={{
        position: 'absolute',
        left: 60,
        right: 60,
        bottom: t.vertical ? 400 : 70,
        textAlign: 'center',
        fontFamily: fonts.sans,
        fontWeight: 600,
        fontSize: t.sub,
        color: brand.ink,
        opacity: o,
        lineHeight: 1.2,
      }}
    >
      {text}
    </div>
  );
};
