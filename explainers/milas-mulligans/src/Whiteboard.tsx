import React from 'react';
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {brand, fonts, steps, T_TITLE, T_STEP, T_END} from './brand';
import {TitleCard, EndCard, clamp, useType} from './common';

// One simple line drawing per scene, viewBox 0 0 400 400, strokes only (no fills).
const drawings: string[][] = [
  // 1 Sign up: clipboard form with a check
  [
    'M110 70 H290 Q310 70 310 90 V350 Q310 370 290 370 H110 Q90 370 90 350 V90 Q90 70 110 70 Z',
    'M160 50 H240 V90 H160 Z',
    'M130 150 H270',
    'M130 200 H270',
    'M130 250 H210',
    'M130 310 L155 335 L200 285',
  ],
  // 2 Tee off: flag on the green, ball near the cup
  [
    'M200 345 V60',
    'M200 60 L300 95 L200 130',
    'M140 345 Q200 330 260 345 Q200 360 140 345 Z',
    'M110 314 A16 16 0 1 0 110.01 314',
  ],
  // 3 Every dollar: coin with a dollar sign
  [
    'M200 90 A110 110 0 1 0 200.01 90',
    'M240 150 Q230 128 200 128 Q160 128 160 160 Q160 190 200 200 Q240 210 240 240 Q240 272 200 272 Q168 272 158 248',
    'M200 108 V292',
  ],
  // 4 A scholarship: graduation cap with tassel
  [
    'M200 90 L340 150 L200 210 L60 150 Z',
    'M120 180 V250 Q200 290 280 250 V180',
    'M200 150 L330 156 V236',
  ],
];

const DRAW = 60; // frames to draw one illustration (2 s)
const LABEL_IN = 45;

const Drawing: React.FC<{paths: string[]}> = ({paths}) => {
  const f = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const vertical = height > width;
  const size = vertical ? 760 : 560;
  const per = DRAW / paths.length;
  return (
    <svg
      viewBox="0 0 400 400"
      width={size}
      height={size}
      style={{position: 'absolute', left: (width - size) / 2, top: vertical ? 330 : 70}}
    >
      {paths.map((d, i) => {
        const p = interpolate(f, [i * per, (i + 1) * per], [0, 1], clamp);
        return (
          <path
            key={i}
            d={d}
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - p}
            opacity={p > 0 ? 1 : 0}
            fill="none"
            stroke={brand.ink}
            strokeWidth={8}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        );
      })}
    </svg>
  );
};

const WBScene: React.FC<{i: number}> = ({i}) => {
  const f = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const t = useType();
  const vertical = height > width;
  const o = interpolate(f, [LABEL_IN, LABEL_IN + 10], [0, 1], clamp);
  const out = interpolate(f, [T_STEP - 8, T_STEP], [1, 0], clamp);
  return (
    <AbsoluteFill style={{opacity: out}}>
      <Drawing paths={drawings[i]} />
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: vertical ? 1130 : 640,
          textAlign: 'center',
          fontFamily: fonts.sans,
          fontWeight: 800,
          fontSize: t.label * 1.15,
          color: brand.navy,
          opacity: o,
        }}
      >
        {steps[i].title}
      </div>
      <div
        style={{
          position: 'absolute',
          left: 60,
          right: 60,
          top: (vertical ? 1130 : 640) + t.label * 1.15 * 1.35,
          textAlign: 'center',
          fontFamily: fonts.sans,
          fontWeight: 600,
          fontSize: t.sub,
          color: brand.ink,
          opacity: interpolate(f, [LABEL_IN + 6, LABEL_IN + 16], [0, 1], clamp),
          lineHeight: 1.2,
        }}
      >
        {steps[i].sub}
      </div>
    </AbsoluteFill>
  );
};

export const Whiteboard: React.FC = () => (
  <AbsoluteFill style={{background: brand.paper}}>
    <Sequence durationInFrames={T_TITLE}>
      <TitleCard />
    </Sequence>
    {steps.map((_, i) => (
      <Sequence key={i} from={T_TITLE + i * T_STEP} durationInFrames={T_STEP}>
        <WBScene i={i} />
      </Sequence>
    ))}
    <Sequence from={T_TITLE + T_STEP * steps.length} durationInFrames={T_END}>
      <EndCard />
    </Sequence>
  </AbsoluteFill>
);
