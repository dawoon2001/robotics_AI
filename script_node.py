import omni
from pxr import UsdGeom, Gf

LED_ROOT = "/World/duckiebot/chassis/led"

COLOR = {
    "red":   (1.0, 0.0, 0.0),
    "green": (0.0, 1.0, 0.0),
    "blue":  (0.0, 0.0, 1.0),
    "white": (1.0, 1.0, 1.0),
}

def _set_color_on_prim_and_children(stage, root_path, rgb):
    root = stage.GetPrimAtPath(root_path)
    if not root.IsValid():
        return False

    changed = 0
    # root 포함 + 모든 자식 순회
    stack = [root]
    while stack:
        p = stack.pop()
        for c in p.GetChildren():
            stack.append(c)

        if not p.IsA(UsdGeom.Gprim):
            continue

        g = UsdGeom.Gprim(p)
        g.CreateDisplayColorAttr().Set([Gf.Vec3f(*rgb)])
        g.CreateDisplayOpacityAttr().Set([1.0])
        changed += 1

    return changed > 0

def compute(db):
    stage = omni.usd.get_context().get_stage()
    if stage is None:
        return

    cmd = str(db.inputs.cmd).strip().lower()
    if cmd not in COLOR:
        db.log_warn(f"[LED] Unknown cmd: {cmd}")
        return

    ok = _set_color_on_prim_and_children(stage, LED_ROOT, COLOR[cmd])
    if not ok:
        db.log_warn(f"[LED] No Gprim found under: {LED_ROOT}")
        return

    db.log_warn(f"[LED] led subtree -> {cmd}")
