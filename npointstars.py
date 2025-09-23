# ******************************************************************************
# Copyright (c) 2025. All rights reserved.
#
# This work is licensed under the Creative Commons Attribution 4.0
# International License. To view a copy of this license,
# visit # http://creativecommons.org/licenses/by/4.0/.
# Author: roximn <roximn@rixir.org>
# ******************************************************************************
from typing import Callable, Sequence

from manim import *
from manim import SVGNAMES
from numpy.typing import NDArray

# ******************************************************************************
config.frame_width = 9
config.frame_height = 16
config.frame_size = (1080, 1920)

GridColor: ParsableManimColor = "#003049"
ConstructionLineColor: ParsableManimColor = "#FF9911"
ReferenceDotColor: ParsableManimColor = "#D62828"
IndicateDotColor: ParsableManimColor = "#9DD9D2"
LabelSize: float = 24.0
LabelFillColor: ParsableManimColor = "#EAE2B7"
FinalColor: ParsableManimColor = "#392F5A"
InstructionColor: ParsableManimColor = SVGNAMES.BROWN

# ******************************************************************************
def TexWrappedText(txt: str, *,
                   parent: Mobject | None = None,
                   fontSize: str = "normalsize",
                   italic: bool = True,
                   bold: bool = False,
                   center: bool = True,
                   color: ParsableManimColor = BLACK,
                   width: int = 170) -> Tex:
    """Create a wrapped text with specified font size, style and alignment.

    Args:
        txt (str): The text to be displayed.
        parent (MObject, optional): The parent object below which the text is placed.
        fontSize (str, optional): Font size. One of "tiny", "small", "normalsize",
            "large", "Large", "LARGE", "huge", "Huge". Default is "normalsize".
        italic (bool, optional): If True, the text will be in italics. Default
            is True.
        bold (bool, optional): If True, the text will be in bold. Default
            is False.
        center (bool, optional): If True, the text will be centered. Default
            is True.
        color (ParsableManimColor, optional): The color of the text. Default is BLACK.
        width (int, optional): The width of the text box. Default is 180.

    Returns:
        Tex: A Tex MObject with the wrapped text and specified attributes.
    """
    assert fontSize in ('tiny', 'small', 'normalsize', 'large', 'Large', 'LARGE', 'huge', 'Huge')
    texText = txt
    if bold:
        texText = f"\\textbf{{{texText}}}"
    if italic:
        texText = f"\\textit{{{texText}}}"
    if center:
        texText = r"\centering" + texText
    texText = fr"\{fontSize} {texText}"
    texText = Tex(r"\parbox{" f"{width}" "px}{" f"{texText}" "}",
                  tex_template=TexFontTemplates.palatino, color=color)
    if parent is not None:
        texText.next_to(parent, DOWN)
    return texText

# ******************************************************************************
def createInstruction(txt: str, continued: bool = False, parent: Mobject | None = None):
    if hasattr(createInstruction, "instructionCount"):
        n = createInstruction.instructionCount
    else:
        createInstruction.instructionCount = 0

    if continued:
        instruction = TexWrappedText(txt, color=InstructionColor, parent=parent)
    else:
        createInstruction.instructionCount += 1
        instruction = TexWrappedText(
            f"{createInstruction.instructionCount}. {txt}",
            color=InstructionColor,
            parent=parent
        )
    return instruction

# ******************************************************************************
def XY(point: NDArray[np.float64]) -> NDArray[np.float64]:
    """Get X, Y coordinates of the point, discarding the Z coordinate"""
    return np.array([point[0], point[1], 0])

# ******************************************************************************
def intersections(points: Sequence[NDArray[np.float64]],
                  interval: int, sides: int) -> list[NDArray[np.float64]]:
    """Get intersections of the lines joining the list of points on a circle at given interval

    Args:
        points (Sequence[NDArray[np.float64]]): A sequence of points that lie on a circle.
        interval (int): The interval between the points to be joined.
        sides (int): The number of sides of the polygon formed by joining every `interval`-th point.

    Returns:
        list[NDArray[np.float64]]: A list of intersection points of the lines joining every `interval`-th pair of points.
    """
    CAP: Callable[[int], int] = lambda x: x % len(points)
    pp: list[NDArray[np.float64]] = []
    for i in range(sides):
        a1 = points[CAP(i)]
        a2 = points[CAP(i + interval)]
        b1 = points[CAP(i + 1)]
        b2 = points[CAP(i + 1 - interval)]
        intersection = line_intersection([XY(a1), XY(a2)], [XY(b1), XY(b2)])
        pp.append(intersection)
    return pp

# ******************************************************************************
def dashed(mobject: VMobject, factor: float=1.0) -> DashedVMobject:
    """Return a dashed version of the given VMobject.

    Args:
        mobject (VMobject): The Mobject to be dashed.
        factor (float, optional): A scaling factor for the number of dashes,
            for base value of 64 dashes and a ratio of 0.6 for
            the dash length to space length. Default is 1.0.

    Returns:
        DashedVMobject: A new Mobject that is a dashed version of the input.
    """
    return DashedVMobject(mobject, num_dashes=int(64 * factor), dashed_ratio=0.6)

# ==============================================================================
class SixPointStar(Scene):
    def construct(self):
        # **********************************************************************
        # Configuration
        # **********************************************************************
        RADIUS: float = 3.0

        background = ImageMobject("assets/paper-texture-02.jpg")
        background.scale_to_fit_height(self.camera.frame_height)
        background.set_z_index(-100)
        self.add(background)

        # **********************************************************************
        # Construction
        # **********************************************************************
        plane = NumberPlane(
            x_range=(-4, +4), y_range=(-4, +4),
            axis_config={'stroke_color': GridColor},
            background_line_style={
                "stroke_color": GridColor,
                "stroke_opacity": 0.25
            })
        baseline = Line(np.array([-4, 0, 0]), np.array([+4, 0, 0]),
                        color=ConstructionLineColor)

        centralDot = (Dot(color=ReferenceDotColor)
                      .move_to(np.array([0, 0, 0])))
        centralCircle = (Circle(radius=RADIUS, color=ConstructionLineColor)
                         .move_to(np.array([0, 0, 0])))

        dotA = Dot(color=ReferenceDotColor).move_to(np.array([-RADIUS, 0, 0]))
        arcA = dashed(Arc(radius=RADIUS, arc_center=np.array([-RADIUS, 0, 0]),
                          start_angle=PI * 3 / 2, angle=PI,
                          color=ConstructionLineColor))
        dotB = (Dot(color=ReferenceDotColor)
                .move_to(np.array([+RADIUS, 0, 0])))
        arcB = dashed(Arc(radius=RADIUS,  arc_center=np.array([+RADIUS, 0, 0]),
                          start_angle=PI * 1 / 2, angle=PI,
                          color=ConstructionLineColor))

        sixPoints: list[NDArray[np.float64]] = [
            spherical_to_cartesian([RADIUS, n * DEGREES, 90 * DEGREES])
            for n in range(0, 360, 60)
        ]
        sixDots = VGroup(*[Dot(p, color=ReferenceDotColor) for p in sixPoints])
        enumeratedLocations: list[tuple[int, NDArray[np.float64]]] = [
            (i, p) for i, p in enumerate(
                spherical_to_cartesian([RADIUS + 0.5, n * DEGREES, 90 * DEGREES])
                for n in range(0, 360, 60))
        ]
        sixLabels = VGroup(*[
            LabeledDot(label=Text(str(i + 1), color=ReferenceDotColor, font_size=LabelSize),
                       point=p, fill_color=LabelFillColor)
            for i, p in enumeratedLocations
        ])

        triPoints = sixPoints[:]
        triPoints.append(sixPoints[0])
        tri1 = dashed(Polygon(*triPoints[0::2], color=ConstructionLineColor))
        tri2 = dashed(Polygon(*triPoints[1::2], color=ConstructionLineColor))

        interPoints: list[NDArray[np.float64]] = intersections(sixPoints, interval=2, sides=6)
        sixPointStarVertices: list[NDArray[np.float64]] = []
        for a, b in zip(sixPoints, interPoints):
            sixPointStarVertices.extend([a, b])
        sixPointVertexDots = [Dot(p, radius=DEFAULT_DOT_RADIUS*0.75, color=FinalColor)
                              for p in sixPointStarVertices]
        sixPointStar = Polygon(*sixPointStarVertices, color=FinalColor, fill_opacity=1)

        howto = (TexWrappedText('how to draw a', fontSize='Large', color=FinalColor, italic=True, bold=False)
                 .next_to(sixPointStar, UP)).shift(np.array((0.0, 0.5, 0.0)))
        title = (TexWrappedText('Six-Point Star', fontSize='huge',
                                color=FinalColor, italic=False, bold=True)
                 .next_to(sixPointStar, DOWN)).shift(np.array((0.0, -0.5, 0.0)))

        # **********************************************************************
        # Animation
        # **********************************************************************
        self.add(title, howto, sixPointStar)
        self.wait(2)

        self.play(FadeOut(title), FadeOut(howto),
                  FadeOut(sixPointStar), FadeIn(plane))
        self.wait(1)

        # Step 1
        ins1 = createInstruction('Draw a straight line', parent=plane)
        self.play(FadeIn(ins1, shift=UP))
        self.play(Create(baseline))

        # Step 2
        ins2 = createInstruction('Draw a circle on the line', parent=plane)
        self.play(Transform(ins1, ins2))
        self.play(FadeIn(centralDot))
        self.play(Create(centralCircle))
        self.wait(1)

        # Step 3A
        ins3A = createInstruction('From the intersection of the line and circle, draw arcs cutting the circle.', parent=plane)
        self.play(Transform(ins1, ins3A), FadeIn(dotA), FadeIn(dotB))
        self.play(FadeIn(dotA), FadeIn(dotB))
        self.play(Flash(dotA, color=ReferenceDotColor), Flash(dotB, color=ReferenceDotColor))
        self.play(Create(arcA), Create(arcB))
        self.wait(1)

        # Step 3B

        ins3B = createInstruction('this creates six points on the circle', continued=True, parent=plane)
        self.play(baseline.animate.fade(0.5), Transform(ins1, ins3B))
        self.play(baseline.animate.fade(0.75), centralDot.animate.fade(0.75),
                  FadeIn(sixDots), FadeIn(sixLabels),
                  FadeOut(dotA), FadeOut(dotB))
        self.play(*[Flash(d, color=ReferenceDotColor) for d in sixDots])
        self.wait(1)

        # Step 4
        ins4 = createInstruction('Join the alternate dots,\ncreating two triangles', parent=plane)
        self.play(centralCircle.animate.fade(0.5), arcA.animate.fade(0.5), arcB.animate.fade(0.5),
                  Transform(ins1, ins4))
        self.play(centralCircle.animate.fade(0.75), arcA.animate.fade(0.75), arcB.animate.fade(0.75))
        self.play(Create(tri1), run_time=2)
        self.play(Create(tri2), run_time=2)
        self.wait(1)

        # Step 5
        ins5 = createInstruction('Draw along the outline of the two triangles to create the 6-point star', parent=plane)
        self.play(tri1.animate.fade(0.5), tri2.animate.fade(0.5), FadeOut(sixLabels), FadeOut(sixDots), Transform(ins1, ins5),
                  *[FadeIn(d, scale=1.5) for d in sixPointVertexDots])
        sixPointStar.set_fill(FinalColor, opacity=0)
        self.play(Create(sixPointStar), run_time=5)
        self.play(*[FadeOut(d) for d in sixPointVertexDots],
                  FadeOut(arcA), FadeOut(arcB),
                  FadeOut(tri1), FadeOut(tri2), FadeOut(ins1),
                  FadeOut(baseline), FadeOut(centralCircle), FadeOut(centralDot), FadeOut(plane),
                  FadeIn(title), sixPointStar.animate.set_fill(FinalColor, opacity=1), run_time=2)

        self.wait(2)


# ==============================================================================
class EightPointStar(Scene):
    def construct(self):
        # **********************************************************************
        # Configuration
        # **********************************************************************
        RADIUS: float = 2.0

        background = ImageMobject("assets/paper-texture-02.jpg")
        background.scale_to_fit_height(self.camera.frame_height)
        background.set_z_index(-100)
        self.add(background)

        # **********************************************************************
        # Construction
        # **********************************************************************
        plane = NumberPlane(
            x_range=(-4, +4), y_range=(-4, +4),
            axis_config={'stroke_color': GridColor},
            background_line_style={
                "stroke_color": GridColor,
                "stroke_opacity": 0.25
            })
        baseline = Line(np.array([-4, 0, 0]), np.array([+4, 0, 0]),
                        color=ConstructionLineColor)

        centralDot = (Dot(color=ReferenceDotColor)
                      .move_to(np.array([0, 0, 0])))
        centralCircle = (Circle(radius=RADIUS, color=ConstructionLineColor)
                         .move_to(np.array([0, 0, 0])))
        dashedCentralCircle = dashed(centralCircle, factor=1.0)

        pointA = (+RADIUS, 0, 0)
        dotA = Dot(color=ReferenceDotColor).move_to(pointA)
        arcA = dashed(Arc(radius=RADIUS, arc_center=pointA,
                          start_angle=(90 - 5) * DEGREES, angle=(180 + 10) * DEGREES,
                          color=ConstructionLineColor), factor=0.5)

        pointB = (-RADIUS, 0, 0)
        dotB = Dot(color=ReferenceDotColor).move_to(pointB)
        arcB = dashed(Arc(radius=RADIUS, arc_center=pointB,
                          start_angle=(270 - 5) * DEGREES, angle=(180 + 10) * DEGREES,
                          color=ConstructionLineColor), factor=0.5)

        fourPoints = [spherical_to_cartesian([RADIUS, n * DEGREES, 90 * DEGREES])
                      for n in [60, 120, 240, 300]]
        fourDots = VGroup(*[Dot(p, color=ReferenceDotColor) for p in fourPoints])
        enumeratedLocations: list[tuple[int, NDArray[np.float64]]] = [
            (i, p) for i, p in enumerate(
                spherical_to_cartesian([RADIUS + 0.5, n * DEGREES, 90 * DEGREES])
                for n in [60, 120, 240, 300])
        ]
        fourLabels = VGroup(*[
            LabeledDot(label=Text('abcd'[i], color=RED, font_size=16),
                       point=p, fill_color=LabelFillColor)
            for i, p in enumeratedLocations
        ])

        upperArcR = dashed(Arc(radius=RADIUS, arc_center=fourPoints[0],
                               start_angle=(120 - 5) * DEGREES, angle=10*DEGREES,
                               color=ConstructionLineColor), factor=0.1)
        upperArcL = dashed(Arc(radius=RADIUS, arc_center=fourPoints[1],
                               start_angle=(60 - 5) * DEGREES, angle=10*DEGREES,
                               color=ConstructionLineColor), factor=0.1)
        lowerArcL = dashed(Arc(radius=RADIUS, arc_center=fourPoints[2],
                               start_angle=(300 - 5) * DEGREES, angle=10*DEGREES,
                               color=ConstructionLineColor), factor=0.1)
        lowerArcR = dashed(Arc(radius=RADIUS, arc_center=fourPoints[3],
                               start_angle=(240 - 5) * DEGREES, angle=10*DEGREES,
                               color=ConstructionLineColor), factor=0.1)
        for a in (upperArcR, upperArcL, lowerArcL, lowerArcR):
            a.z_index = 10

        pointC = pointA + spherical_to_cartesian([RADIUS * 2, 120 * DEGREES, 90 * DEGREES])
        pointD = pointA + spherical_to_cartesian([RADIUS * 2, 240 * DEGREES, 90 * DEGREES])
        dotC = Dot(color=ReferenceDotColor).move_to(pointC)
        dotD = Dot(color=ReferenceDotColor).move_to(pointD)
        perpendicularLine = dashed(Line(pointC, pointD, color=ConstructionLineColor), factor=0.8)

        pointE = centralCircle.point_at_angle(90 * DEGREES)
        pointF = centralCircle.point_at_angle(270 * DEGREES)
        dotE = Dot(color=ReferenceDotColor).move_to(pointE)
        dotF = Dot(color=ReferenceDotColor).move_to(pointF)
        arcE = dashed(Arc(radius=RADIUS, arc_center=pointE,
                          start_angle=(180 - 5) * DEGREES, angle=(180 + 10) * DEGREES,
                          color=ConstructionLineColor), factor=0.5)
        arcF = dashed(Arc(radius=RADIUS, arc_center=pointF,
                          start_angle=(0 - 5) * DEGREES, angle=(180 + 10) * DEGREES,
                          color=ConstructionLineColor), factor=0.5)

        cornerPoints = []
        for p in [pointA, pointB]:
            c = Circle(radius=RADIUS).move_to(p)
            for a in [90, 270]:
                cornerPoints.append(c.point_at_angle(a * DEGREES))
        cornerPoints.append(cornerPoints.pop(1))
        cornerDots = VGroup(*[Dot(p, color=ReferenceDotColor) for p in cornerPoints])
        crossLineA = dashed(Line(cornerPoints[0], cornerPoints[2], color=ConstructionLineColor), factor=0.8)
        crossLineB = dashed(Line(cornerPoints[1], cornerPoints[3], color=ConstructionLineColor), factor=0.8)

        eightPoints = [spherical_to_cartesian([RADIUS, n * DEGREES, 90 * DEGREES]) for n in range(0, 360, 45)]
        eightDots = [Dot(p, color=ReferenceDotColor) for p in eightPoints]

        squarePoints = eightPoints[:]
        squarePoints.append(eightPoints[0])

        sq1 = dashed(Polygon(*squarePoints[0::2], color=ConstructionLineColor), factor=0.8)
        sq2 = dashed(Polygon(*squarePoints[1::2], color=ConstructionLineColor), factor=0.8)

        interPoints = intersections(eightPoints, interval=2, sides=8)
        eightPointStarVertices = []
        for a, b in zip(eightPoints, interPoints):
            eightPointStarVertices.extend([a, b])
        eightPointVertexDots = [Dot(p, radius=DEFAULT_DOT_RADIUS*0.75, color=FinalColor)
                                for p in eightPointStarVertices]
        eightPointStar = Polygon(*eightPointStarVertices, color=FinalColor, fill_opacity=1)

        howto = (TexWrappedText('how to draw a', fontSize='Large', color=FinalColor, italic=True, bold=False)
                 .next_to(eightPointStar, UP)).shift(np.array((0.0, 0.5, 0.0)))
        title = (TexWrappedText('Eight-Point Star', fontSize='huge',
                                color=FinalColor, italic=False, bold=True)
                 .next_to(eightPointStar, DOWN)).shift(np.array((0.0, -0.5, 0.0)))

        # **********************************************************************
        # Animation
        self.add(title, howto, eightPointStar)
        self.wait(2)

        self.play(FadeOut(title), FadeOut(howto), FadeOut(eightPointStar),
                  FadeIn(plane))
        self.wait(1)

        # Step 1
        ins1 = createInstruction('Draw a straight line', parent=plane)
        self.play(FadeIn(ins1, shift=UP))
        self.play(Create(baseline))

        # Step 2
        ins2 = createInstruction('Draw a circle on the line', parent=plane)
        self.play(Transform(ins1, ins2))
        self.play(Indicate(centralDot, color=IndicateDotColor, scale_factor=1.5))
        self.play(Create(dashedCentralCircle))
        self.wait(1)

        # Step 3
        ins3 = createInstruction('From the intersection of the line and circle, draw arcs cutting the circle.', parent=plane)
        self.play(Transform(ins1, ins3), FadeIn(dotA), FadeIn(dotB))
        self.play(Indicate(dotA, color=IndicateDotColor, scale_factor=1.5))
        self.play(Create(arcA))
        self.play(Indicate(dotB, color=IndicateDotColor, scale_factor=1.5))
        self.play(Create(arcB))
        self.wait(1)

        # Step 4
        ins4 = createInstruction('Draw perpendicular to the baseline.', parent=plane)
        self.play(Transform(ins1, ins4), baseline.animate.fade(0.75), centralDot.animate.fade(0.75))
        self.play(Indicate(fourDots[0], color=IndicateDotColor, scale_factor=1.5))
        self.play(Create(upperArcR), run_time=0.3)
        self.play(Indicate(fourDots[1], color=IndicateDotColor, scale_factor=1.5))
        self.play(Create(upperArcL), run_time=0.3)
        self.wait(0.5)
        self.play(Indicate(fourDots[2], color=IndicateDotColor, scale_factor=1.5))
        self.play(Create(lowerArcL), run_time=0.3)
        self.play(Indicate(fourDots[3], color=IndicateDotColor, scale_factor=1.5))
        self.play(Create(lowerArcR), run_time=0.3)
        self.play(fourDots.animate.fade(0.75))
        self.play(Indicate(dotC, color=IndicateDotColor, scale_factor=1.5),
                  Indicate(dotD, color=IndicateDotColor, scale_factor=1.5))
        self.play(Create(perpendicularLine))
        self.wait(1)

        # Step 5
        ins5 = createInstruction('From the intersection of the perpendicular line '
                                 'and the circle, draw arcs cutting the previous two arcs.',
                                 parent=plane)
        self.remove(fourDots)
        self.play(Transform(ins1, ins5), FadeIn(dotE), FadeIn(dotF),
                  *[arc.animate.fade(0.75) for arc in (upperArcR, upperArcL, lowerArcL, lowerArcR)],
                  FadeOut(dotC), FadeOut(dotD))
        self.play(Indicate(dotE, color=IndicateDotColor, scale_factor=1.5))
        self.play(Create(arcE))
        self.play(Indicate(dotF, color=IndicateDotColor, scale_factor=1.5))
        self.play(Create(arcF))
        self.wait(1)

        # Step 6
        ins6 = createInstruction('Draw diagonal lines intersecting the circle.',
                                 parent=plane)
        self.play(Transform(ins1, ins6), perpendicularLine.animate.fade(0.75),
                  FadeIn(cornerDots),
                  *[arc.animate.fade(0.75) for arc in (arcA, arcB, arcE, arcF)])
        self.play(Indicate(cornerDots[0], color=IndicateDotColor, scale_factor=1.5),
                  Indicate(cornerDots[2], color=IndicateDotColor, scale_factor=1.5))
        self.play(Create(crossLineA))
        self.play(Indicate(cornerDots[1], color=IndicateDotColor, scale_factor=1.5),
                  Indicate(cornerDots[3], color=IndicateDotColor, scale_factor=1.5))
        self.play(Create(crossLineB))
        self.wait(1)

        # Step 7
        ins7 = createInstruction('Draw diagonal lines intersecting the circle.',
                                 parent=plane)
        self.play(Transform(ins1, ins7), FadeOut(cornerDots),
                  *[line.animate.fade(0.75) for line in (crossLineA, crossLineB)],
                  *[FadeIn(d) for d in eightDots])
        self.remove(dotA, dotB, dotE, dotF)

        # Step 8
        ins8 = createInstruction('This creates eight equally spaced points '
                                 'on the circle. Join alternate points to '
                                 'create two overlapping squares.',
                                 parent=plane)
        self.play(Transform(ins1, ins8), dashedCentralCircle.animate.fade(0.5))
        self.play(*[Indicate(d, color=IndicateDotColor, scale_factor=1.5)
                    for d in eightDots[0::2]])
        self.play(Create(sq1))

        self.play(*[Indicate(d, color=IndicateDotColor, scale_factor=1.5)
                    for d in eightDots[1::2]])
        self.play(Create(sq2))

        # Step 9
        ins9 = createInstruction('Draw along the outline of the two squares '
                                 'to create the 8-point star',
                                 parent=plane)
        self.play(Transform(ins1, ins9))
        self.play(*[o.animate.fade(0.75) for o in eightDots],
          *[o.animate.fade(0.50) for o in (sq1, sq2)],
          *[FadeIn(d) for d in eightPointVertexDots])
        eightPointStar.set_fill(FinalColor, opacity=0)
        self.play(Create(eightPointStar), run_time=3)
        self.play(FadeOut(sq1), FadeOut(sq2), FadeOut(ins1),
                  *[FadeOut(d) for d in (*eightPointVertexDots, sq1, sq2, *eightDots)],
                  *[FadeOut(d) for d in (arcA, arcB, arcE, arcF, crossLineA, crossLineB)],
                  *[FadeOut(d) for d in (perpendicularLine, upperArcR, upperArcL, lowerArcL, lowerArcR)],
                  *[FadeOut(d) for d in (baseline, centralDot, dashedCentralCircle, plane)],
                  FadeIn(title),
                  eightPointStar.animate.set_fill(FinalColor, opacity=1), run_time=2)
        self.wait(1)


# ==============================================================================
class EightPointStarConcept(Scene):
    def construct(self):
        RADIUS = 2.0

        plane = NumberPlane(x_range=(-4, +4), y_range=(-4, +4)).set_opacity(0.25)
        baseline = dashed(Line((-3, 0, 0), (+3, 0, 0), color=YELLOW), factor=0.8)

        centralDot = Dot(color=RED).move_to((0, 0, 0))
        centralCircle = Circle(radius=RADIUS, color=YELLOW).move_to((0, 0, 0))
        dashedCentralCircle = dashed(centralCircle, factor=1.0)

        eightPoints = [spherical_to_cartesian([RADIUS, n * DEGREES, 90 * DEGREES]) for n in range(0, 360, 45)]
        eightDots = [Dot(p, color=RED) for p in eightPoints]
        eightLabels = VGroup(*[LabeledDot(label=Text(str(i+1), color=RED, font_size=16), point=p, fill_color=WHITE)
                               for i, p in enumerate(spherical_to_cartesian([RADIUS + 0.5, n * DEGREES, 90 * DEGREES])
                                                     for n in range(0, 360, 45))])

        squarePoints = eightPoints[:]
        squarePoints.append(eightPoints[0])

        sq1 = dashed(Polygon(*squarePoints[0::2], color=BLUE), factor=0.8)
        sq2 = dashed(Polygon(*squarePoints[1::2], color=BLUE), factor=0.8)

        interPoints = intersections(eightPoints, interval=2, sides=8)
        eightPointStarVertices = []
        for a, b in zip(eightPoints, interPoints):
            eightPointStarVertices.extend([a, b])
        eightPointVertexDots = [Dot(p, color=BLUE) for p in eightPointStarVertices]
        eightPointStar = Polygon(*eightPointStarVertices, color=BLUE, fill_opacity=1)

        title = Text('Core Concept', color=BLUE, slant='ITALIC').next_to(eightPointStar, UP)
        self.add(plane, title, eightPointStar)
        # self.wait(2)

        self.play(*[FadeOut(o) for o in (title, eightPointStar)],
                  *[FadeIn(o) for o in (plane, centralDot, dashedCentralCircle)])
        # self.wait()

        eightDots.insert(0, eightDots[0].copy())
        eightLabels.insert(0, eightLabels[0].copy())
        # self.play(FadeIn(eightDots[0]))
        for i in range(0, 8):
            self.play(Transform(eightDots[i], eightDots[i+1]),
                      FadeIn(eightLabels[i+1]),
                      run_time=0.3)
        self.play(*[FadeOut(o) for o in eightLabels])
        # self.wait()

        self.play(DrawBorderThenFill(sq1))
        self.play(DrawBorderThenFill(sq2))
        # self.wait()

        self.play(*[FadeOut(o) for o in (dashedCentralCircle, *eightDots, sq1, sq2)],
                  *[FadeIn(o) for o in (eightPointStar,)])

        self.wait(5)

# ==============================================================================
