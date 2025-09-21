from typing import Callable, Sequence
from manim import *
from manim.typing import Point3DLike
from manim import SVGNAMES
from numpy.typing import NDArray

config.frame_width = 9
config.frame_height = 16
config.frame_size = (1080, 1920)

instructionCount = 0


def createInstruction(txt: str, continued: bool = False):
    global instructionCount

    if continued:
        instruction = Text(txt, font='Arial', font_size=24, color=SVGNAMES.BROWN)
    else:
        instructionCount += 1
        instruction = Text(f'{instructionCount}. {txt}', font='Corbel', font_size=24, color=SVGNAMES.BROWN)
    return instruction


def XY(point: NDArray[np.float64]) -> NDArray[np.float64]:
    """Get X, Y coordinates of the point discarding the Z coordinate"""
    return np.array([point[0], point[1], 0])


def intersections(points: Sequence[NDArray[np.float64]], interval: int, sides: int) -> list[NDArray[np.float64]]:
    """Get intersections of the lines joining the list of points on a circle at given inteval"""
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


def dashed(mobject: VMobject, factor: float=1.0):
    return DashedVMobject(mobject, num_dashes=int(64 * factor), dashed_ratio=0.6)


class SixPointStar(Scene):
    def createCircle(self, center: Point3DLike | Mobject,
                     radius: float, color: ParsableManimColor=WHITE,
                     dotColor: ParsableManimColor=RED):
        dot = Dot(color=dotColor).move_to(center)
        circle = Circle(radius=radius, color=color).move_to(center)

        self.add(dot)
        return circle

    def construct(self):
        background = ImageMobject("assets/paper-texture-02.jpg")
        background.scale_to_fit_height(self.camera.frame_height)
        background.set_z_index(-100)
        self.add(background)

        RADIUS: float = 3.0
        GridColor: ParsableManimColor = SVGNAMES.DIMGRAY
        ConstructionLineColor: ParsableManimColor = SVGNAMES.DARKGREEN
        ReferenceDotColor: ParsableManimColor = SVGNAMES.CRIMSON
        LabelSize: float = 24.0
        LabelFillColor: ParsableManimColor = SVGNAMES.CORNSILK
        FinalColor: ParsableManimColor = SVGNAMES.ROYALBLUE
        

        plane = NumberPlane(
            x_range=(-4, +4), y_range=(-4, +4),
            axis_config={'stroke_color': GridColor},
            background_line_style={
                "stroke_color": GridColor,
                "stroke_opacity": 0.25
            })
        baseline = dashed(Line(np.array([-4, 0, 0]), np.array([+4, 0, 0]), color=ConstructionLineColor))

        centralDot = Dot(color=ReferenceDotColor).move_to(np.array([0, 0, 0]))
        centralCircle = Circle(radius=RADIUS, color=ConstructionLineColor).move_to(np.array([0, 0, 0]))

        dotA = Dot(color=ReferenceDotColor).move_to(np.array([-RADIUS, 0, 0]))
        arcA = dashed(Arc(radius=RADIUS, start_angle=PI * 3 / 2, angle=PI, arc_center=np.array([-RADIUS, 0, 0]), color=ConstructionLineColor))
        dotB = Dot(color=ReferenceDotColor).move_to(np.array([+RADIUS, 0, 0]))
        arcB = dashed(Arc(radius=RADIUS, start_angle=PI * 1 / 2, angle=PI, arc_center=np.array([+RADIUS, 0, 0]), color=ConstructionLineColor))

        sixPoints: list[NDArray[np.float64]] = [spherical_to_cartesian([RADIUS, n * DEGREES, 90 * DEGREES]) for n in range(0, 360, 60)]
        sixDots = VGroup(*[Dot(p, color=ReferenceDotColor) for p in sixPoints])
        sixLabels = VGroup(*[LabeledDot(label=Text(str(i + 1), color=ReferenceDotColor, font_size=LabelSize), point=p, fill_color=LabelFillColor)
                             for i, p in enumerate(spherical_to_cartesian([RADIUS + 0.5, n * DEGREES, 90 * DEGREES])
                                                   for n in range(0, 360, 60))])

        triPoints = sixPoints[:]
        triPoints.append(sixPoints[0])
        tri1 = dashed(Polygon(*triPoints[0::2], color=ConstructionLineColor))
        tri2 = dashed(Polygon(*triPoints[1::2], color=ConstructionLineColor))

        interPoints: list[NDArray[np.float64]] = intersections(sixPoints, interval=2, sides=6)
        sixPointStarVertices: list[NDArray[np.float64]] = []
        for a, b in zip(sixPoints, interPoints):
            sixPointStarVertices.extend([a, b])
        sixPointVertexDots = [Dot(p, radius=DEFAULT_DOT_RADIUS*0.75, color=FinalColor) for p in sixPointStarVertices]
        sixPointStar = Polygon(*sixPointStarVertices, color=FinalColor, fill_opacity=1)

        title = Text('Six-Point Star', color=FinalColor).next_to(sixPointStar, DOWN)
        howto = Text('how to draw a', color=FinalColor, slant='ITALIC').next_to(sixPointStar, UP)
        self.add(title, howto, sixPointStar)
        self.wait(2)

        self.play(FadeOut(title), FadeOut(howto), FadeOut(sixPointStar), FadeIn(plane))
        self.wait()

        # Step 1
        # ins1 = createInstruction('Draw a straight line')
        # self.play(FadeIn(ins1, shift=UP))
        self.play(Create(baseline))

        # Step 2
        # ins2 = createInstruction('Draw a circle on the line')
        # self.play(Transform(ins1, ins2))
        self.play(FadeIn(centralDot))
        self.play(Create(centralCircle))
        self.wait(1)

        # Step 3A
        # ins3A = createInstruction('From the intersection of the line and circle, draw arcs cutting the circle.')
        # self.play(Transform(ins1, ins3A), FadeIn(dotA), FadeIn(dotB))
        self.play(FadeIn(dotA), FadeIn(dotB))
        self.play(Flash(dotA, color=ReferenceDotColor), Flash(dotB, color=ReferenceDotColor))
        self.play(Create(arcA), Create(arcB))
        self.wait(1)

        # Step 3B

        # ins3B = createInstruction('this creates six points on the circle', continued=True)
        # self.play(baseline.animate.fade(0.5), Transform(ins1, ins3B))
        self.play(baseline.animate.fade(0.75), centralDot.animate.fade(0.75),
                  FadeIn(sixDots), FadeIn(sixLabels),
                  FadeOut(dotA), FadeOut(dotB))
        self.play(*[Flash(d, color=ReferenceDotColor) for d in sixDots])
        self.wait(1)

        # Step 4
        # ins4 = createInstruction('Join the alternate dots, creating two triangles')
        # self.play(centralCircle.animate.fade(0.5), arcA.animate.fade(0.5), arcB.animate.fade(0.5),
        # Transform(ins1, ins4))
        self.play(centralCircle.animate.fade(0.75), arcA.animate.fade(0.75), arcB.animate.fade(0.75))
        self.play(Create(tri1), run_time=2)
        self.play(Create(tri2), run_time=2)
        self.wait(1)

        # Step 5
        # ins5 = createInstruction('Draw along the outline of the two triangles to create the 6-point star')
        # self.play(tri1.animate.fade(0.5), tri2.animate.fade(0.5), FadeOut(sixLabels), Transform(ins1, ins5))
        self.play(tri1.animate.fade(0.75), tri2.animate.fade(0.75),
                  FadeOut(sixLabels), FadeOut(sixDots),
                  *[FadeIn(d, scale=1.5) for d in sixPointVertexDots], run_time=1)
        sixPointStar.set_fill(FinalColor, opacity=0)
        self.play(Create(sixPointStar), run_time=5)
        self.play(*[FadeOut(d) for d in sixPointVertexDots],
                  FadeOut(arcA), FadeOut(arcB),
                  FadeOut(tri1), FadeOut(tri2),
                  FadeOut(baseline), FadeOut(centralCircle), FadeOut(centralDot), FadeOut(plane),
                  FadeIn(title), sixPointStar.animate.set_fill(FinalColor, opacity=1), run_time=2)

        # ins6 = createInstruction('Six-Point Rosette', continued=True)
        # self.play(FadeOut(ins1), FadeIn(ins6, scale=1.5), run_time=2)
        self.wait(2)
        self.play(FadeOut(title), FadeOut(sixPointStar))


class EightPointStar(Scene):
    def construct(self):
        # **************************************************************************************************************
        # Construction
        RADIUS = 2.0

        plane = NumberPlane(x_range=(-4, +4), y_range=(-4, +4)).set_opacity(0.25)
        baseline = dashed(Line([-3, 0, 0], [+3, 0, 0], color=YELLOW), factor=0.8)

        centralDot = Dot(color=RED).move_to([0, 0, 0])
        centralCircle = Circle(radius=RADIUS, color=YELLOW).move_to([0, 0, 0])
        dashedCentralCircle = dashed(centralCircle, factor=1.0)

        pointA = [+RADIUS, 0, 0]
        dotA = Dot(color=RED).move_to(pointA)
        arcA = dashed(Arc(radius=RADIUS, start_angle=(90 - 5) * DEGREES, angle=(180 + 10) * DEGREES,
                          arc_center=pointA, color=YELLOW), factor=0.5)

        pointB = [-RADIUS, 0, 0]
        dotB = Dot(color=RED).move_to(pointB)
        arcB = dashed(Arc(radius=RADIUS, start_angle=(270 - 5) * DEGREES, angle=(180 + 10) * DEGREES,
                          arc_center=pointB, color=YELLOW), factor=0.5)

        fourPoints = [spherical_to_cartesian([RADIUS, n * DEGREES, 90 * DEGREES]) for n in [60, 120, 240, 300]]
        fourDots = VGroup(*[Dot(p, color=RED) for p in fourPoints])
        fourLabels = VGroup(*[LabeledDot(label=Text('abcd'[i], color=RED, font_size=16), point=p, fill_color=WHITE)
                              for i, p in enumerate(spherical_to_cartesian([RADIUS + 0.5, n * DEGREES, 90 * DEGREES])
                                                    for n in [60, 120, 240, 300])])

        upperArcR = dashed(Arc(radius=RADIUS, start_angle=(120 - 5) * DEGREES, angle=10*DEGREES,
                               arc_center=fourPoints[0], color=YELLOW), factor=0.1)
        upperArcL = dashed(Arc(radius=RADIUS, start_angle=(60 - 5) * DEGREES, angle=10*DEGREES,
                               arc_center=fourPoints[1], color=YELLOW), factor=0.1)
        lowerArcL = dashed(Arc(radius=RADIUS, start_angle=(300 - 5) * DEGREES, angle=10*DEGREES,
                               arc_center=fourPoints[2], color=YELLOW), factor=0.1)
        lowerArcR = dashed(Arc(radius=RADIUS, start_angle=(240 - 5) * DEGREES, angle=10*DEGREES,
                               arc_center=fourPoints[3], color=YELLOW), factor=0.1)
        for a in (upperArcR, upperArcL, lowerArcL, lowerArcR):
            a.z_index = 10

        pointC = pointA + spherical_to_cartesian([RADIUS * 2, 120 * DEGREES, 90 * DEGREES])
        pointD = pointA + spherical_to_cartesian([RADIUS * 2, 240 * DEGREES, 90 * DEGREES])
        dotC = Dot(color=RED).move_to(pointC)
        dotD = Dot(color=RED).move_to(pointD)
        perpendicularLine = dashed(Line(pointC, pointD, color=YELLOW), factor=0.8)

        pointE = centralCircle.point_at_angle(90 * DEGREES)
        pointF = centralCircle.point_at_angle(270 * DEGREES)
        dotE = Dot(color=RED).move_to(pointE)
        dotF = Dot(color=RED).move_to(pointF)
        arcE = dashed(Arc(radius=RADIUS, start_angle=(180 - 5) * DEGREES, angle=(180 + 10) * DEGREES,
                          arc_center=pointE, color=YELLOW), factor=0.5)
        arcF = dashed(Arc(radius=RADIUS, start_angle=(0 - 5) * DEGREES, angle=(180 + 10) * DEGREES,
                          arc_center=pointF, color=YELLOW), factor=0.5)

        cornerPoints = []
        for p in [pointA, pointB]:
            c = Circle(radius=RADIUS).move_to(p)
            for a in [90, 270]:
                cornerPoints.append(c.point_at_angle(a * DEGREES))
        cornerPoints.append(cornerPoints.pop(1))
        cornerDots = VGroup(*[Dot(p, color=RED) for p in cornerPoints])
        crossLineA = dashed(Line(cornerPoints[0], cornerPoints[2], color=YELLOW), factor=0.8)
        crossLineB = dashed(Line(cornerPoints[1], cornerPoints[3], color=YELLOW), factor=0.8)

        eightPoints = [spherical_to_cartesian([RADIUS, n * DEGREES, 90 * DEGREES]) for n in range(0, 360, 45)]
        eightDots = [Dot(p, color=RED) for p in eightPoints]

        squarePoints = eightPoints[:]
        squarePoints.append(eightPoints[0])

        sq1 = dashed(Polygon(*squarePoints[0::2], color=YELLOW), factor=0.8)
        sq2 = dashed(Polygon(*squarePoints[1::2], color=YELLOW), factor=0.8)

        interPoints = intersections(eightPoints, interval=2, sides=8)
        eightPointStarVertices = []
        for a, b in zip(eightPoints, interPoints):
            eightPointStarVertices.extend([a, b])
        eightPointVertexDots = [Dot(p, color=BLUE) for p in eightPointStarVertices]
        eightPointStar = Polygon(*eightPointStarVertices, color=BLUE, fill_opacity=1)

        # **************************************************************************************************************
        # Animation
        title = Text('Eight-Point Star', color=BLUE).next_to(eightPointStar, DOWN)
        howto = Text('how to draw an', color=BLUE, slant='ITALIC').next_to(eightPointStar, UP)
        self.add(title, howto, eightPointStar)
        # self.wait(2)

        self.play(FadeOut(title), FadeOut(howto), FadeOut(eightPointStar), FadeIn(plane))
        # self.wait()

        # Step 1
        self.play(Create(baseline))

        # Step 2
        self.play(Indicate(centralDot, color=BLUE, scale_factor=1.5))
        self.play(Create(dashedCentralCircle))
        # self.wait(1)

        # Step 3
        self.play(Indicate(dotA, color=BLUE, scale_factor=1.5))
        self.play(Create(arcA))
        self.play(Indicate(dotB, color=BLUE, scale_factor=1.5))
        self.play(Create(arcB))
        # self.wait(1)

        # Step 4
        self.play(baseline.animate.fade(0.75), centralDot.animate.fade(0.75))
        self.play(Indicate(fourDots[0], color=BLUE, scale_factor=1.5))
        self.play(Create(upperArcR), run_time=0.3)
        self.play(Indicate(fourDots[1], color=BLUE, scale_factor=1.5))
        self.play(Create(upperArcL), run_time=0.3)
        # self.wait(0.5)
        self.play(Indicate(fourDots[2], color=BLUE, scale_factor=1.5))
        self.play(Create(lowerArcL), run_time=0.3)
        self.play(Indicate(fourDots[3], color=BLUE, scale_factor=1.5))
        self.play(Create(lowerArcR), run_time=0.3)
        # self.wait(0.5)

        # Step 5
        self.play(fourDots.animate.fade(0.75))
        self.play(Indicate(dotC, color=BLUE, scale_factor=1.5),
                  Indicate(dotD, color=BLUE, scale_factor=1.5))
        self.play(Create(perpendicularLine))
        # self.wait(1)

        # Step 6
        self.remove(fourDots)
        self.play(FadeIn(dotE), FadeIn(dotF),
                  *[arc.animate.fade(0.75) for arc in (upperArcR, upperArcL, lowerArcL, lowerArcR)],
                  FadeOut(dotC), FadeOut(dotD))
        self.play(Indicate(dotE, color=BLUE, scale_factor=1.5))
        self.play(Create(arcE))
        self.play(Indicate(dotF, color=BLUE, scale_factor=1.5))
        self.play(Create(arcF))
        self.wait(0.5)

        # Step 7
        self.play(perpendicularLine.animate.fade(0.75),
                  FadeIn(cornerDots),
                  *[arc.animate.fade(0.75) for arc in (arcA, arcB, arcE, arcF)])
        self.play(Indicate(cornerDots[0], color=BLUE, scale_factor=1.5),
                  Indicate(cornerDots[2], color=BLUE, scale_factor=1.5))
        self.play(Create(crossLineA))
        self.play(Indicate(cornerDots[1], color=BLUE, scale_factor=1.5),
                  Indicate(cornerDots[3], color=BLUE, scale_factor=1.5))
        self.play(Create(crossLineB))
        # self.wait()

        # Step 8
        self.play(FadeOut(cornerDots),
                  *[line.animate.fade(0.75) for line in (crossLineA, crossLineB)],
                  *[FadeIn(d) for d in eightDots])
        self.remove(dotA, dotB, dotE, dotF)

        self.play(*[Indicate(d, color=BLUE, scale_factor=1.5) for d in eightDots[0::2]])
        self.play(Create(sq1))

        self.play(*[Indicate(d, color=BLUE, scale_factor=1.5) for d in eightDots[1::2]])
        self.play(Create(sq2))

        # Step 9
        self.play(*[o.animate.fade(0.75) for o in eightDots],
                  *[o.animate.fade(0.50) for o in (sq1, sq2)],
                  *[FadeIn(d) for d in eightPointVertexDots])
        eightPointStar.set_fill(BLUE, opacity=0)
        self.play(Create(eightPointStar), run_time=3)
        self.play(FadeOut(sq1), FadeOut(sq2),
                  *[FadeOut(d) for d in (*eightPointVertexDots, sq1, sq2, *eightDots)],
                  *[FadeOut(d) for d in (arcA, arcB, arcE, arcF, crossLineA, crossLineB)],
                  *[FadeOut(d) for d in (perpendicularLine, upperArcR, upperArcL, lowerArcL, lowerArcR)],
                  *[FadeOut(d) for d in (baseline, centralDot, dashedCentralCircle, plane)],
                  FadeIn(title),
                  eightPointStar.animate.set_fill(BLUE, opacity=1), run_time=2)
        self.wait()


# **************************************************************************************************************
class EightPointStarConcept(Scene):
    def construct(self):
        RADIUS = 2.0

        plane = NumberPlane(x_range=(-4, +4), y_range=(-4, +4)).set_opacity(0.25)
        baseline = dashed(Line([-3, 0, 0], [+3, 0, 0], color=YELLOW), factor=0.8)

        centralDot = Dot(color=RED).move_to([0, 0, 0])
        centralCircle = Circle(radius=RADIUS, color=YELLOW).move_to([0, 0, 0])
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

# **************************************************************************************************************
