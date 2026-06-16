# CyGlobs Fast and Furious Example

This example integrates the CyGlobsGL MVP / clip-space pipeline into the CyGlobs Python Framework For Full-Stack Developers repo.

It is a safe simulated street-race rendering example inspired by cinematic racing language, not copied movie assets.

## Pipeline Directive

```text
#ifndef Sort io To Jecht
Translate To Daq
Rotate To MVP
Scale To Cap
#endif
```

## Bit Field Packing

Each directive is encoded as a 16-bit hex word:

```text
bits 15..12 = opcode
bits 11..8  = sort/io channel
bits 7..4   = transform channel
bits 3..0   = cap/scale channel
```

## Render Objects

The example builds abstract classes for the pipeline:

- `AbstractSceneObject`
- `RaceCar`
- `SafetyCube`
- `CheckpointCube`
- `Track`
- `Framebuffer`
- `ClipSpacePipeline`
- `StreetRaceScene`

## Scene

The scene uses:

- radius `.62`
- point-in-time vector `(0.62, 0.0, 1.0)`
- red solid cube restraint value `.62`
- blue wireframe race-car geometry
- green dashed rotated cube MVP target
- street race track shell
- model -> view -> projection -> clip-space output

## Run

From the repository root:

```bash
python examples/cyglobs_fast_and_furious_example/fast_street_race_pipeline.py
```

The script prints an ASCII framebuffer and writes:

```text
cyglobs_fast_and_furious_framebuffer.txt
```
