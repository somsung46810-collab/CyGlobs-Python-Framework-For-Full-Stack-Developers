from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from math import cos, radians, sin, tan
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

Vec3 = Tuple[float, float, float]
Vec4 = Tuple[float, float, float, float]
Edge = Tuple[int, int]


@dataclass(frozen=True)
class BitFieldInstruction:
    """16-bit packed CyGlobsGL directive.

    Layout:
    - bits 15..12 opcode
    - bits 11..8  sort/io channel
    - bits 7..4   transform channel
    - bits 3..0   cap/scale channel
    """

    opcode: int
    sort_channel: int
    transform_channel: int
    cap_channel: int

    @classmethod
    def from_word(cls, word: int) -> "BitFieldInstruction":
        return cls((word >> 12) & 0xF, (word >> 8) & 0xF, (word >> 4) & 0xF, word & 0xF)

    def to_word(self) -> int:
        return ((self.opcode & 0xF) << 12) | ((self.sort_channel & 0xF) << 8) | ((self.transform_channel & 0xF) << 4) | (self.cap_channel & 0xF)


class BitFieldPacker:
    """Hex editing + bit-field packing for ifndef/sort/translate/rotate/scale/endif."""

    OPCODES = {
        "ifndef_sort_io_to_jecht": 0x1,
        "translate_to_daq": 0x2,
        "rotate_to_mvp": 0x3,
        "scale_to_cap": 0x4,
        "endif": 0xF,
    }

    @classmethod
    def pack(cls, name: str, sort: int = 0, transform: int = 0, cap: int = 0) -> str:
        return f"0x{BitFieldInstruction(cls.OPCODES[name], sort, transform, cap).to_word():04X}"

    @staticmethod
    def unpack(hex_word: str) -> BitFieldInstruction:
        return BitFieldInstruction.from_word(int(hex_word, 16))


class Matrix4:
    def __init__(self, rows: Sequence[Sequence[float]]):
        self.rows = [[float(v) for v in row] for row in rows]

    @staticmethod
    def identity() -> "Matrix4":
        return Matrix4([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

    @staticmethod
    def translation(x: float, y: float, z: float) -> "Matrix4":
        return Matrix4([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]])

    @staticmethod
    def scale(s: float) -> "Matrix4":
        return Matrix4([[s, 0, 0, 0], [0, s, 0, 0], [0, 0, s, 0], [0, 0, 0, 1]])

    @staticmethod
    def rotation_y(degrees: float) -> "Matrix4":
        a = radians(degrees)
        return Matrix4([[cos(a), 0, sin(a), 0], [0, 1, 0, 0], [-sin(a), 0, cos(a), 0], [0, 0, 0, 1]])

    @staticmethod
    def perspective(fov_deg: float, aspect: float, near: float, far: float) -> "Matrix4":
        f = 1.0 / tan(radians(fov_deg) / 2.0)
        return Matrix4([[f / aspect, 0, 0, 0], [0, f, 0, 0], [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)], [0, 0, -1, 0]])

    def __matmul__(self, other: "Matrix4") -> "Matrix4":
        return Matrix4([[sum(self.rows[r][k] * other.rows[k][c] for k in range(4)) for c in range(4)] for r in range(4)])

    def transform(self, v: Vec4) -> Vec4:
        return tuple(sum(self.rows[r][c] * v[c] for c in range(4)) for r in range(4))  # type: ignore[return-value]


@dataclass
class AbstractSceneObject(ABC):
    name: str
    vertices: List[Vec3]
    edges: List[Edge]
    model: Matrix4 = field(default_factory=Matrix4.identity)
    line_style: str = "solid"

    @abstractmethod
    def semantic_role(self) -> str:
        raise NotImplementedError

    def clip_vertices(self, mvp: Matrix4) -> List[Vec3]:
        out: List[Vec3] = []
        for x, y, z in self.vertices:
            cx, cy, cz, cw = mvp.transform((x, y, z, 1.0))
            out.append((cx, cy, cz) if abs(cw) < 1e-6 else (cx / cw, cy / cw, cz / cw))
        return out


class RaceCar(AbstractSceneObject):
    def semantic_role(self) -> str:
        return "blue wireframe race car pipelined to clip space"


class SafetyCube(AbstractSceneObject):
    def semantic_role(self) -> str:
        return "red solid cube restraint bounding value"


class CheckpointCube(AbstractSceneObject):
    def semantic_role(self) -> str:
        return "green dashed rotated cube transform checkpoint"


class Track(AbstractSceneObject):
    def semantic_role(self) -> str:
        return "street-race road shell"


def cube_vertices(radius: float = 0.62) -> tuple[list[Vec3], list[Edge]]:
    r = radius
    verts = [(-r, -r, -r), (r, -r, -r), (r, r, -r), (-r, r, -r), (-r, -r, r), (r, -r, r), (r, r, r), (-r, r, r)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
    return verts, edges


class Framebuffer:
    def __init__(self, width: int = 96, height: int = 40):
        self.width = width
        self.height = height
        self.clear()

    def clear(self) -> None:
        self.pixels = [[" " for _ in range(self.width)] for _ in range(self.height)]

    def line_ndc(self, a: Vec3, b: Vec3, ch: str) -> None:
        ax = int((a[0] + 1) * 0.5 * (self.width - 1)); ay = int((1 - (a[1] + 1) * 0.5) * (self.height - 1))
        bx = int((b[0] + 1) * 0.5 * (self.width - 1)); by = int((1 - (b[1] + 1) * 0.5) * (self.height - 1))
        steps = max(abs(bx - ax), abs(by - ay), 1)
        for i in range(steps + 1):
            t = i / steps
            x = int(ax + (bx - ax) * t); y = int(ay + (by - ay) * t)
            if 0 <= x < self.width and 0 <= y < self.height:
                self.pixels[y][x] = ch

    def text(self) -> str:
        return "\n".join("".join(row).rstrip() for row in self.pixels)


class ClipSpacePipeline:
    def __init__(self, width: int = 96, height: int = 40):
        self.framebuffer = Framebuffer(width, height)
        self.projection = Matrix4.perspective(65, width / height, 0.1, 100)
        self.view = Matrix4.translation(0, -0.2, -6)

    def render(self, objects: Iterable[AbstractSceneObject]) -> str:
        self.framebuffer.clear()
        for obj in objects:
            mvp = self.projection @ self.view @ obj.model
            clipped = obj.clip_vertices(mvp)
            ch = "#" if isinstance(obj, RaceCar) else "R" if isinstance(obj, SafetyCube) else "G" if isinstance(obj, CheckpointCube) else "."
            for a, b in obj.edges:
                self.framebuffer.line_ndc(clipped[a], clipped[b], ch)
        return self.framebuffer.text()


@dataclass
class StreetRaceScene:
    objects: List[AbstractSceneObject]
    instructions: List[str]
    point_time_vector: Vec3 = (0.62, 0.0, 1.0)
    restraint_value: float = 0.62

    def render_ascii(self) -> str:
        return ClipSpacePipeline().render(self.objects)

    def save(self, path: str | Path) -> Path:
        p = Path(path)
        p.write_text(self.render_ascii(), encoding="utf-8")
        return p


def build_fast_race_scene(radius: float = 0.62) -> StreetRaceScene:
    verts, edges = cube_vertices(radius)
    car = RaceCar("ifndef.blue_wireframe.car", verts, edges, Matrix4.translation(-0.55, -0.25, 0) @ Matrix4.scale(0.72))
    bounds = SafetyCube("red_solid_cube.restraint", verts, edges, Matrix4.translation(-0.55, -0.25, 0) @ Matrix4.scale(0.92))
    checkpoint = CheckpointCube("green_dashed_rotated_cube.mvp_target", verts, edges, Matrix4.translation(0.85, -0.18, -0.25) @ Matrix4.rotation_y(35) @ Matrix4.scale(0.9), "dashed")
    road = Track("street_race.track_shell", [(-3, -0.9, 0), (3, -0.9, 0), (3, -0.9, 6), (-3, -0.9, 6)], [(0, 1), (1, 2), (2, 3), (3, 0)], Matrix4.identity())
    instructions = [
        BitFieldPacker.pack("ifndef_sort_io_to_jecht", sort=1, transform=0, cap=6),
        BitFieldPacker.pack("translate_to_daq", sort=2, transform=1, cap=2),
        BitFieldPacker.pack("rotate_to_mvp", sort=3, transform=6, cap=2),
        BitFieldPacker.pack("scale_to_cap", sort=4, transform=0, cap=6),
        BitFieldPacker.pack("endif", sort=0, transform=0, cap=0),
    ]
    return StreetRaceScene([road, bounds, car, checkpoint], instructions)


def main() -> None:
    scene = build_fast_race_scene(radius=0.62)
    print("CyGlobs Fast and Furious Example / Hex Bit-Field Stream")
    print(" ".join(scene.instructions))
    print(scene.render_ascii())
    scene.save("cyglobs_fast_and_furious_framebuffer.txt")


if __name__ == "__main__":
    main()
