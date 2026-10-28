import React from "react";
import {
  AbsoluteFill,
  Composition,
  Easing,
  OffthreadVideo,
  Sequence,
  interpolate,
  registerRoot,
  staticFile,
  useCurrentFrame,
  continueRender,
  delayRender,
} from "remotion";

// Holmes Place recovery demo: 16:9, 21s, silent, Hebrew RTL.

const FPS = 30;
const RED = "#CF4948";
const INK = "#0E0B0B";

const HE = "U+0590-05FF,U+200C-2010,U+20AA,U+25CC,U+FB1D-FB4F";
const LAT =
  "U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+2000-206F,U+20AC,U+2122,U+2212,U+FEFF,U+FFFD";

const fontCss = [300, 500, 800]
  .flatMap((w) => [
    `@font-face{font-family:Heebo;font-weight:${w};src:url(${staticFile(`holmes/fonts/heebo-hebrew-${w}-normal.woff2`)}) format("woff2");unicode-range:${HE};}`,
    `@font-face{font-family:Heebo;font-weight:${w};src:url(${staticFile(`holmes/fonts/heebo-latin-${w}-normal.woff2`)}) format("woff2");unicode-range:${LAT};}`,
  ])
  .concat(
    `@font-face{font-family:Playfair;font-weight:400 900;src:url(${staticFile("holmes/fonts/PlayfairDisplay-latin.woff2")}) format("woff2");}`,
  )
  .join("\n");

const ease = Easing.bezier(0.16, 1, 0.3, 1);

// Fade + rise in at `at` (frames, relative to the sequence), fade out before `end`.
const useReveal = (at: number, end: number, rise = 40) => {
  const f = useCurrentFrame();
  const inP = interpolate(f, [at, at + 18], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: ease });
  const outP = interpolate(f, [end - 10, end], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return { opacity: inP * outP, transform: `translateY(${(1 - inP) * rise}px)` };
};

const Text: React.FC<{ at: number; end: number; style: React.CSSProperties; children: React.ReactNode }> = ({ at, end, style, children }) => {
  const r = useReveal(at, end);
  return <div style={{ ...style, ...r }}>{children}</div>;
};

const Footage: React.FC<{ start: number; dim: number; dur: number }> = ({ start, dim, dur }) => {
  const f = useCurrentFrame();
  const scale = interpolate(f, [0, dur], [1.04, 1.12]);
  return (
    <AbsoluteFill>
      <OffthreadVideo
        src={staticFile("holmes/cabin.mp4")}
        startFrom={Math.round(start * FPS)}
        muted
        style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${scale})` }}
      />
      <AbsoluteFill
        style={{ background: `radial-gradient(ellipse at 50% 55%, rgba(14,11,11,${dim - 0.25}) 0%, rgba(14,11,11,${dim}) 70%)` }}
      />
    </AbsoluteFill>
  );
};

const Brand: React.FC = () => (
  <div
    style={{
      position: "absolute", top: 64, left: 80, fontFamily: "Playfair", color: "#fff",
      fontSize: 26, letterSpacing: 8, opacity: 0.85, direction: "ltr",
    }}
  >
    HOLMES PLACE
  </div>
);

const center: React.CSSProperties = {
  direction: "rtl", fontFamily: "Heebo", color: "#fff", textAlign: "center",
  display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
};

const SceneHook: React.FC<{ dur: number }> = ({ dur }) => (
  <AbsoluteFill>
    <Footage start={0} dim={0.6} dur={dur} />
    <Brand />
    <AbsoluteFill style={center}>
      <Text at={8} end={dur} style={{ fontSize: 44, fontWeight: 300, letterSpacing: 1 }}>הולמס פלייס מביאה את</Text>
      <Text at={16} end={dur} style={{ fontSize: 120, fontWeight: 800, lineHeight: 1.1, marginTop: 8 }}>
        מהפכת ה-<span style={{ color: RED, letterSpacing: 10 }}>RECOVERY</span>
      </Text>
      <Text at={28} end={dur} style={{ fontSize: 44, fontWeight: 300, marginTop: 8 }}>לישראל</Text>
    </AbsoluteFill>
  </AbsoluteFill>
);

const ScenePromise: React.FC<{ dur: number }> = ({ dur }) => (
  <AbsoluteFill>
    <Footage start={8} dim={0.68} dur={dur} />
    <Brand />
    <AbsoluteFill style={center}>
      <Text at={6} end={dur} style={{ fontSize: 84, fontWeight: 300 }}>אל תתאמנו קשה יותר.</Text>
      <Text at={36} end={dur} style={{ fontSize: 108, fontWeight: 800, color: RED, marginTop: 12 }}>תתאוששו חכם יותר.</Text>
    </AbsoluteFill>
  </AbsoluteFill>
);

const ITEMS = [
  { n: "01", t: "תא אור אדום", s: "שיקום ותחושת רעננות" },
  { n: "02", t: "אמבט קרח", s: "להפיק יותר מכל אימון" },
  { n: "03", t: "עיסוי בלחץ אוויר", s: "פחות נפיחות וכבדות" },
];

const SceneMenu: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame();
  const line = interpolate(f, [4, 30], [0, 1], { extrapolateRight: "clamp", easing: ease });
  return (
    <AbsoluteFill style={{ background: INK }}>
      <Brand />
      <AbsoluteFill style={{ ...center, justifyContent: "center" }}>
        <Text at={0} end={dur} style={{ fontSize: 40, fontWeight: 500, letterSpacing: 2 }}>
          ב-<span style={{ color: RED, letterSpacing: 6 }}>RECOVERY</span> משתמשים בטכנולוגיות מתקדמות
        </Text>
        <div style={{ width: 1500 * line, height: 2, background: RED, margin: "48px 0 72px" }} />
        <div style={{ display: "flex", gap: 90 }}>
          {ITEMS.map((it, i) => (
            <Text key={it.n} at={14 + i * 12} end={dur} style={{ width: 420, textAlign: "right" }}>
              <div style={{ fontSize: 30, fontWeight: 500, color: RED, letterSpacing: 4, direction: "ltr", textAlign: "right" }}>{it.n}</div>
              <div style={{ fontSize: 56, fontWeight: 800, marginTop: 10, whiteSpace: "nowrap" }}>{it.t}</div>
              <div style={{ fontSize: 32, fontWeight: 300, marginTop: 10, opacity: 0.75 }}>{it.s}</div>
            </Text>
          ))}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const SceneBenefits: React.FC<{ dur: number }> = ({ dur }) => (
  <AbsoluteFill>
    <Footage start={2} dim={0.66} dur={dur} />
    <Brand />
    <AbsoluteFill style={center}>
      {["פחות סטרס.", "שינה עמוקה.", "יותר אנרגיה."].map((t, i) => (
        <Text key={t} at={6 + i * 14} end={dur} style={{ fontSize: 100, fontWeight: 800, lineHeight: 1.2, color: i === 2 ? RED : "#fff" }}>
          {t}
        </Text>
      ))}
      <Text at={54} end={dur} style={{ fontSize: 40, fontWeight: 300, marginTop: 28 }}>החלק שמשלים את האימון</Text>
    </AbsoluteFill>
  </AbsoluteFill>
);

const SceneEnd: React.FC<{ dur: number }> = ({ dur }) => {
  const f = useCurrentFrame();
  const wipe = interpolate(f, [0, 16], [0, 100], { extrapolateRight: "clamp", easing: ease });
  return (
    <AbsoluteFill style={{ background: INK }}>
      <AbsoluteFill style={{ background: RED, clipPath: `circle(${wipe * 1.2}% at 50% 50%)` }} />
      <AbsoluteFill style={center}>
        <Text at={10} end={dur + 20} style={{ fontFamily: "Playfair", fontSize: 130, letterSpacing: 26, lineHeight: 1.05, direction: "ltr" }}>
          HOLMES
          <br />
          PLACE
        </Text>
        <div style={{ height: 50 }} />
        <Text at={26} end={dur + 20} style={{ fontSize: 46, fontWeight: 300 }}>
          בואו לחוות את מהפכת ה-<span style={{ fontWeight: 800, letterSpacing: 4 }}>RECOVERY</span>
        </Text>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const SCENES: [React.FC<{ dur: number }>, number][] = [
  [SceneHook, 4.5],
  [ScenePromise, 4],
  [SceneMenu, 5],
  [SceneBenefits, 4],
  [SceneEnd, 3.5],
];
const TOTAL = SCENES.reduce((a, [, d]) => a + Math.round(d * FPS), 0);

export const HolmesDemo: React.FC = () => {
  const [handle] = React.useState(() => delayRender("fonts"));
  React.useEffect(() => {
    const probes = ["300 40px Heebo", "500 40px Heebo", "800 40px Heebo", "40px Playfair"];
    Promise.all(probes.flatMap((p) => [document.fonts.load(p, "אב"), document.fonts.load(p, "AB")]))
      .then(() => continueRender(handle));
  }, [handle]);
  let from = 0;
  return (
    <AbsoluteFill style={{ background: INK }}>
      <style>{fontCss}</style>
      {SCENES.map(([Scene, d], i) => {
        const dur = Math.round(d * FPS);
        const el = (
          <Sequence key={i} from={from} durationInFrames={dur}>
            <Scene dur={dur} />
          </Sequence>
        );
        from += dur;
        return el;
      })}
    </AbsoluteFill>
  );
};

const Root: React.FC = () => (
  <>
    <Composition id="HolmesDemo" component={HolmesDemo} durationInFrames={TOTAL} fps={FPS} width={1920} height={1080} />
  </>
);

registerRoot(Root);
