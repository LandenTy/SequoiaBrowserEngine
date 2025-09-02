"""
svg.py

Description: Parses SVG elements (rect and path) and provides functions to draw
them onto a Pygame surface. Designed to integrate with a DOM rendering engine.
"""
import pygame, re, math

# --- CONFIG ---
SAMPLES = 30        # cubic bezier samples
LINE_SAMPLES = 10   # line interpolation samples
ARC_SEGMENTS = 5    # rounded rectangle corner segments
MARGIN = 0          # margin inside bounding box

# Optional: some basic named colors
COLOR_NAMES = {
    "black": (0,0,0),
    "white": (255,255,255),
    "red": (255,0,0),
    "green": (0,255,0),
    "blue": (0,0,255),
}

# ----------------- Utility functions -----------------

def parse_color(s):
    s = s.strip().lower()
    if s.startswith("#"):
        if len(s) == 7:
            return tuple(int(s[i:i+2],16) for i in (1,3,5))
        elif len(s) == 4:
            return tuple(int(s[i]*2,16) for i in (1,2,3))
    elif s in COLOR_NAMES:
        return COLOR_NAMES[s]
    return (0,0,0)

def lerp(p0,p1,t):
    return (p0[0]*(1-t)+p1[0]*t, p0[1]*(1-t)+p1[1]*t)

def cubic_bezier(p0,p1,p2,p3,t):
    a = lerp(p0,p1,t)
    b = lerp(p1,p2,t)
    c = lerp(p2,p3,t)
    d = lerp(a,b,t)
    e = lerp(b,c,t)
    return lerp(d,e,t)

def interpolate_line(p0, p1, n=LINE_SAMPLES):
    return [lerp(p0, p1, i/n) for i in range(1, n+1)]

# ----------------- Path parsing -----------------

def parse_path(d):
    points = []
    tokens = re.findall(r"[MLCZHVmlczhv]|-?\d+\.?\d*", d)
    i = 0
    current = (0,0)
    start = (0,0)
    while i < len(tokens):
        t = tokens[i]
        if t=='M':
            x=float(tokens[i+1]); y=float(tokens[i+2])
            current=(x,y); start=(x,y); points.append(current); i+=3
        elif t=='L':
            x=float(tokens[i+1]); y=float(tokens[i+2])
            points.extend(interpolate_line(current,(x,y)))
            current=(x,y); i+=3
        elif t=='H':
            x=float(tokens[i+1])
            points.extend(interpolate_line(current,(x,current[1])))
            current=(x,current[1]); i+=2
        elif t=='V':
            y=float(tokens[i+1])
            points.extend(interpolate_line(current,(current[0],y)))
            current=(current[0],y); i+=2
        elif t=='h':
            dx=float(tokens[i+1])
            points.extend(interpolate_line(current,(current[0]+dx,current[1])))
            current=(current[0]+dx,current[1]); i+=2
        elif t=='v':
            dy=float(tokens[i+1])
            points.extend(interpolate_line(current,(current[0],current[1]+dy)))
            current=(current[0],current[1]+dy); i+=2
        elif t=='C':
            x1=float(tokens[i+1]); y1=float(tokens[i+2])
            x2=float(tokens[i+3]); y2=float(tokens[i+4])
            x=float(tokens[i+5]); y=float(tokens[i+6])
            p0=current; p1=(x1,y1); p2=(x2,y2); p3=(x,y)
            for s in range(1,SAMPLES+1):
                t_s=s/SAMPLES; points.append(cubic_bezier(p0,p1,p2,p3,t_s))
            current=p3; i+=7
        elif t=='c':
            dx1=float(tokens[i+1]); dy1=float(tokens[i+2])
            dx2=float(tokens[i+3]); dy2=float(tokens[i+4])
            dx=float(tokens[i+5]); dy=float(tokens[i+6])
            p0=current; p1=(current[0]+dx1,current[1]+dy1)
            p2=(current[0]+dx2,current[1]+dy2); p3=(current[0]+dx,current[1]+dy)
            for s in range(1,SAMPLES+1):
                t_s=s/SAMPLES; points.append(cubic_bezier(p0,p1,p2,p3,t_s))
            current=p3; i+=7
        elif t in ['Z','z']:
            points.extend(interpolate_line(current,start))
            current=start; i+=1
        else:
            i+=1
    return points

# ----------------- Rounded rect -----------------

def rounded_rect_points(x,y,w,h,radius=0):
    x,y,w,h,radius=float(x),float(y),float(w),float(h),float(radius)
    if radius<=0: return [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
    pts=[]
    # top-left corner
    for i in range(ARC_SEGMENTS+1):
        theta = math.pi - i*math.pi/(2*ARC_SEGMENTS)
        pts.append((x+radius*(1-math.cos(theta)), y+radius*(1-math.sin(theta))))
    pts.append((x+w-radius, y))
    # top-right corner
    for i in range(ARC_SEGMENTS+1):
        theta = -math.pi/2 + i*math.pi/(2*ARC_SEGMENTS)
        pts.append((x+w-radius+radius*math.cos(theta), y+radius+radius*math.sin(theta)))
    pts.append((x+w, y+h-radius))
    # bottom-right corner
    for i in range(ARC_SEGMENTS+1):
        theta = 0 + i*math.pi/(2*ARC_SEGMENTS)
        pts.append((x+w-radius+radius*math.cos(theta), y+h-radius+radius*math.sin(theta)))
    pts.append((x+radius, y+h))
    # bottom-left corner
    for i in range(ARC_SEGMENTS+1):
        theta = math.pi/2 + i*math.pi/(2*ARC_SEGMENTS)
        pts.append((x+radius*math.cos(theta), y+h-radius+radius*math.sin(theta)))
    pts.append((x, y+radius))
    return pts

# ----------------- SVG parsing -----------------

def parse_svg_file(file_path):
    with open(file_path,"r",encoding="utf-8") as f:
        data=f.read()
    elements=[]
    for match in re.finditer(r'<(path|rect)([^>]*)/>', data):
        tag=match.group(1); attrs=match.group(2)
        if tag=='path':
            d_match=re.search(r'd\s*=\s*"([^"]+)"',attrs,re.IGNORECASE)
            if not d_match: continue
            d=d_match.group(1)
            fill_match=re.search(r'fill\s*=\s*"([^"]+)"',attrs,re.IGNORECASE)
            stroke_match=re.search(r'stroke\s*=\s*"([^"]+)"',attrs,re.IGNORECASE)
            fill=parse_color(fill_match.group(1)) if fill_match else (0,0,0)
            stroke=parse_color(stroke_match.group(1)) if stroke_match else None
            points=parse_path(d)
            elements.append({"fill":fill,"stroke":stroke,"points":points})
        elif tag=='rect':
            fill_match=re.search(r'fill\s*=\s*"([^"]+)"',attrs,re.IGNORECASE)
            x_match=re.search(r'x\s*=\s*"([^"]+)"',attrs,re.IGNORECASE)
            y_match=re.search(r'y\s*=\s*"([^"]+)"',attrs,re.IGNORECASE)
            w_match=re.search(r'width\s*=\s*"([^"]+)"',attrs,re.IGNORECASE)
            h_match=re.search(r'height\s*=\s*"([^"]+)"',attrs,re.IGNORECASE)
            rx_match=re.search(r'rx\s*=\s*"([^"]+)"',attrs,re.IGNORECASE)
            fill=parse_color(fill_match.group(1)) if fill_match else (0,0,0)
            x=float(x_match.group(1)) if x_match else 0
            y=float(y_match.group(1)) if y_match else 0
            w=float(w_match.group(1)) if w_match else 0
            h=float(h_match.group(1)) if h_match else 0
            rx=float(rx_match.group(1)) if rx_match else 0
            points=rounded_rect_points(x,y,w,h,rx)
            elements.append({"fill":fill,"stroke":None,"points":points})
    return elements

# ----------------- Scaling -----------------

def scale_points(elements, w, h, viewBox=(0,0,100,100), margin=MARGIN):
    vx,vy,vw,vh=viewBox
    sx=(w-2*margin)/vw; sy=(h-2*margin)/vh
    new_elements=[]
    for elem in elements:
        pts=elem["points"]
        scaled_pts=[((x-vx)*sx+margin,(y-vy)*sy+margin) for x,y in pts]
        new_elem=elem.copy(); new_elem["points"]=scaled_pts
        new_elements.append(new_elem)
    return new_elements

# ----------------- Polygon fill -----------------

def fill_polygon(surface,points,color):
    if not points: return
    min_y=int(min(y for x,y in points))
    max_y=int(max(y for x,y in points))
    for y in range(min_y,max_y+1):
        intersections=[]
        for i in range(len(points)):
            p1=points[i]; p2=points[(i+1)%len(points)]
            if p1[1]==p2[1]: continue
            if (p1[1]<=y<p2[1]) or (p2[1]<=y<p1[1]):
                x=p1[0]+(y-p1[1])*(p2[0]-p1[0])/(p2[1]-p1[1])
                intersections.append(x)
        intersections.sort()
        for i in range(0,len(intersections),2):
            x_start=int(intersections[i])
            if i+1<len(intersections):
                x_end=int(intersections[i+1])
                pygame.draw.line(surface,color,(x_start,y),(x_end,y))

# ----------------- Drawing -----------------

def draw_svg(elements, surface, offset=(0,0)):
    ox,oy = offset
    for elem in elements:
        pts = [(x+ox, y+oy) for x,y in elem["points"]]
        fill = elem["fill"]
        stroke = elem["stroke"]
        if len(pts) > 2:
            if fill: fill_polygon(surface, pts, fill)
            if stroke:
                for i in range(len(pts)-1):
                    pygame.draw.line(surface, stroke, pts[i], pts[i+1])
                pygame.draw.line(surface, stroke, pts[-1], pts[0])
