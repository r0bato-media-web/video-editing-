import React from 'react';
import {AbsoluteFill, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {brand, fonts, steps, T_TITLE, T_STEP, T_END} from './brand';
import {TitleCard, EndCard, SubBand, clamp, useType} from './common';

type P = {x: number; y: number};

const layout = (w: number, h: number): {pos: P[]; size: number; depth: number; labelSide: 'below' | 'right' | 'left'} => {
  if (h > w) {
    // 9:16 — zigzag down the frame, labels beside each block.
    const xs = [330, 750, 330, 750];
    const ys = [420, 660, 900, 1140];
    return {pos: xs.map((x, i) => ({x, y: ys[i]})), size: 110, depth: 70, labelSide: 'right'};
  }
  // 16:9 — left to right, gently rising, labels under each block.
  const xs = [300, 740, 1180, 1620];
  const ys = [470, 420, 370, 320];
  return {pos: xs.map((x, i) => ({x, y: ys[i]})), size: 110, depth: 70, labelSide: 'below'};
};

const Block: React.FC<{c: P; s: number; d: number; n: number}> = ({c, s, d, n}) => {
  const k = 0.866 * s;
  const top = `${c.x},${c.y - s / 2} ${c.x + k},${c.y} ${c.x},${c.y + s / 2} ${c.x - k},${c.y}`;
  const left = `${c.x - k},${c.y} ${c.x},${c.y + s / 2} ${c.x},${c.y + s / 2 + d} ${c.x - k},${c.y + d}`;
  const right = `${c.x + k},${c.y} ${c.x},${c.y + s / 2} ${c.x},${c.y + s / 2 + d} ${c.x + k},${c.y + d}`;
  return (
    <g>
      <polygon points={left} fill={brand.faceLeft} />
      <polygon points={right} fill={brand.faceRight} />
      <polygon points={top} fill={brand.faceTop} />
      <text
        x={c.x}
        y={c.y + 16}
        textAnchor="middle"
        fontFamily={fonts.sans}
        fontWeight={800}
        fontSize={48}
        fill={brand.white}
      >
        {n}
      </text>
    </g>
  );
};

const IsoScene: React.FC = () => {
  const f = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const t = useType();
  const L = layout(width, height);
  const active = Math.min(steps.length - 1, Math.floor(f / T_STEP));

  return (
    <AbsoluteFill>
      <svg width={width} height={height} style={{position: 'absolute'}}>
        {/* Paths between blocks: drawn as the dot travels. */}
        {L.pos.slice(0, -1).map((p, i) => {
          const q = L.pos[i + 1];
          const startF = i * T_STEP + 55;
          const prog = interpolate(f, [startF, startF + 40], [0, 1], clamp);
          const x = p.x + (q.x - p.x) * prog;
          const y = p.y + (q.y - p.y) * prog;
          if (prog <= 0) return null;
          return (
            <g key={`path${i}`}>
              <line x1={p.x} y1={p.y} x2={x} y2={y} stroke={brand.grey} strokeWidth={6} strokeDasharray="14 12" strokeLinecap="round" />
              {prog < 1 ? <circle cx={x} cy={y} r={16} fill={brand.navy} /> : null}
            </g>
          );
        })}
        {L.pos.map((p, i) => {
          const local = f - i * T_STEP;
          if (local < 0) return null;
          const rise = spring({frame: local, fps, config: {damping: 16, stiffness: 120}});
          const dy = interpolate(rise, [0, 1], [180, 0]);
          return (
            <g key={`b${i}`} transform={`translate(0 ${dy})`} opacity={interpolate(local, [0, 8], [0, 1], clamp)}>
              <Block c={p} s={L.size} d={L.depth} n={i + 1} />
            </g>
          );
        })}
      </svg>
      {/* Step titles: appear on the block's rise and stay. */}
      {L.pos.map((p, i) => {
        const local = f - i * T_STEP;
        if (local < 0) return null;
        const o = interpolate(local, [8, 18], [0, 1], clamp);
        const below = L.labelSide === 'below';
        const style: React.CSSProperties = below
          ? {left: p.x - 220, width: 440, top: p.y + L.size / 2 + L.depth + 24, textAlign: 'center', whiteSpace: 'nowrap'}
          : i % 2 === 0
            ? {left: p.x + 0.866 * L.size + 30, top: p.y - 10, textAlign: 'left', whiteSpace: 'nowrap'}
            : {left: p.x - 0.866 * L.size - 30 - 560, width: 560, top: p.y - 10, textAlign: 'right', whiteSpace: 'nowrap'};
        return (
          <div
            key={`l${i}`}
            style={{
              position: 'absolute',
              fontFamily: fonts.sans,
              fontWeight: 800,
              fontSize: t.label,
              color: i === active ? brand.navy : brand.ink,
              opacity: o,
              ...style,
            }}
          >
            {steps[i].title}
          </div>
        );
      })}
      {steps.map((s, i) => (
        <Sequence key={`sub${i}`} from={i * T_STEP} durationInFrames={T_STEP} layout="none">
          <SubBand text={s.sub} start={10} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const Isometric: React.FC = () => (
  <AbsoluteFill style={{background: brand.paper}}>
    <Sequence durationInFrames={T_TITLE}>
      <TitleCard />
    </Sequence>
    <Sequence from={T_TITLE} durationInFrames={T_STEP * steps.length}>
      <IsoScene />
    </Sequence>
    <Sequence from={T_TITLE + T_STEP * steps.length} durationInFrames={T_END}>
      <EndCard />
    </Sequence>
  </AbsoluteFill>
);
