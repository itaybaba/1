# Holmes Place recovery demo (OpenMontage / Remotion)

Output: `holmes-place-openmontage-demo.mp4` (repo root): 1920x1080, 21s, silent.

To re-render, from an OpenMontage checkout after `make setup`:

```bash
cd remotion-composer
mkdir -p public/holmes/fonts
cp <this repo>/demo/red-light-cabin-orbit.mp4 public/holmes/cabin.mp4
npm install --no-save @fontsource/heebo@5.0.8
for w in 300 500 800; do for s in hebrew latin; do
  cp node_modules/@fontsource/heebo/files/heebo-$s-$w-normal.woff2 public/holmes/fonts/; done; done
cp src/fonts/PlayfairDisplay-latin.woff2 public/holmes/fonts/
cp <this repo>/holmes-place/openmontage/HolmesDemo.tsx src/
npx remotion render src/HolmesDemo.tsx HolmesDemo out.mp4 --codec h264 --crf 18
```
