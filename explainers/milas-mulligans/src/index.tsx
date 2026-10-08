import React from 'react';
import {Composition, registerRoot} from 'remotion';
import {Isometric} from './Isometric';
import {Whiteboard} from './Whiteboard';
import {EndBeat} from './EndBeat';
import {DURATION, FPS} from './brand';

const Root: React.FC = () => (
  <>
    <Composition id="Iso-9x16" component={Isometric} width={1080} height={1920} fps={FPS} durationInFrames={DURATION} />
    <Composition id="Iso-16x9" component={Isometric} width={1920} height={1080} fps={FPS} durationInFrames={DURATION} />
    <Composition id="WB-9x16" component={Whiteboard} width={1080} height={1920} fps={FPS} durationInFrames={DURATION} />
    <Composition id="WB-16x9" component={Whiteboard} width={1920} height={1080} fps={FPS} durationInFrames={DURATION} />
    <Composition id="End-9x16" component={EndBeat} width={1080} height={1920} fps={FPS} durationInFrames={135} />
    <Composition id="End-16x9" component={EndBeat} width={1920} height={1080} fps={FPS} durationInFrames={135} />
  </>
);

registerRoot(Root);
