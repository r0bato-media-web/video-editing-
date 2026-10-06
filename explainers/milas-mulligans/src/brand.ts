// Mila's Mulligans — INTERNAL TEST palette.
// Sampled from the approved "one week out" flyer (Drive: milas_mulligans_one_week_out_time_matched_v2.png)
// because the client logo folder is empty. Replace with logo-file colours when Rob supplies them.
export const brand = {
  navy: '#043375', // bottom bar
  ink: '#1E3151', // dark body text
  grey: '#7B7879', // logo grey
  paper: '#F2F1F0', // flyer background
  white: '#FFFFFF',
  // Isometric face shades derived from navy (no new hues).
  faceTop: '#2C5A9E',
  faceLeft: '#043375',
  faceRight: '#0A2650',
};

export const fonts = {
  // Stand-ins until Rob names the client's fonts: Caladea ~ flyer serif, Inter ~ flyer sans.
  serif: 'Caladea, "Liberation Serif", serif',
  sans: 'Inter, "Liberation Sans", sans-serif',
};

// Every fact below is sourced: approved flyer + milas-mulligans-captions skill.
export const steps = [
  {title: 'Sign up', sub: 'milasmulligans.com'},
  {title: 'Tee off', sub: 'Whitetail Golf Club, Bath PA'},
  {title: 'Every dollar', sub: 'goes to the scholarship'},
  {title: 'A scholarship', sub: 'Arian Walker Hannon-Kohler Memorial Scholarship'},
];

export const titleText = 'Where your mulligan goes';
export const endText = 'We play for Arian.';
export const endUrl = 'milasmulligans.com';

export const FPS = 30;
export const T_TITLE = 75; // 2.5 s
export const T_STEP = 105; // 3.5 s per step
export const T_END = 105; // 3.5 s
export const DURATION = T_TITLE + T_STEP * steps.length + T_END; // 600 = 20 s
