import random
import math

import minecraft
import block
from vec3 import Vec3

leaves = block.LEAVES.withData(2)
wood = block.WOOD.withData(2)

def grow_trunk(mc, loc):
    mc.setBlocks(
        loc.x, loc.y, loc.z,
        loc.x+1, loc.y+10, loc.z+1,
        wood)

def grow_leaves(mc, loc, depth=3):
    mc.setBlock(loc.x, loc.y, loc.z, leaves)
    if depth > 0:
        for offset in map(Vec3,
                [1,-1, 0, 0, 0, 0],
                [0, 0, 1,-1, 0, 0],
                [0, 0, 0, 0, 1,-1]):
            if random.random() > 0.6:
                grow_leaves(mc, loc + offset, depth-1)

def grow_tree(mc, loc):
    for x in range(loc.x-1, loc.x+3):
        for z in range(loc.z-1, loc.z+3):
            grow_leaves(mc, Vec3(x, loc.y+8, z))
            grow_leaves(mc, Vec3(x, loc.y+9, z))
    grow_trunk(mc, loc)

ident_vec = Vec3(1,1,1)

def build_pyramid(mc, loc, w, block_type=block.SANDSTONE):
    if w > 0:
        mc.setBlocks(
                loc.x,     loc.y, loc.z,
                loc.x + w, loc.y, loc.z + w,
                block_type)
        build_pyramid(mc, loc + ident_vec, w - 2, block_type)

def round_up(n):
    if n<0:
        return -round(-n)
    else:
        return round(n)

def magic_block(block_type):
    if block_type == None:
        return block.Block(95, data=random.randint(0,15))
    else:
        return block_type

def make_xy_ring(mc, loc, r, block_type):
    # Loop through until x is bigger than y.
    for x in range(int(r)):
        y = int(round(math.sqrt(r**2 - (x+0.5)**2)))
        if x > y: break
        mc.setBlock( loc.x+x, loc.y+y, loc.z, magic_block(block_type))
        mc.setBlock( loc.x-x, loc.y+y, loc.z, magic_block(block_type))
        mc.setBlock( loc.x+x, loc.y-y, loc.z, magic_block(block_type))
        mc.setBlock( loc.x-x, loc.y-y, loc.z, magic_block(block_type))
        mc.setBlock( loc.x+y, loc.y+x, loc.z, magic_block(block_type))
        mc.setBlock( loc.x-y, loc.y+x, loc.z, magic_block(block_type))
        mc.setBlock( loc.x+y, loc.y-x, loc.z, magic_block(block_type))
        mc.setBlock( loc.x-y, loc.y-x, loc.z, magic_block(block_type))

def make_xz_ring(mc, loc, r, block_type):
    # Loop through until x is bigger than y.
    for x in range(int(r)):
        z = int(round(math.sqrt(r**2 - (x+0.5)**2)))
        if x > z: break
        mc.setBlock( loc.x+x, loc.y, loc.z+z, magic_block(block_type))
        mc.setBlock( loc.x-x, loc.y, loc.z+z, magic_block(block_type))
        mc.setBlock( loc.x+x, loc.y, loc.z-z, magic_block(block_type))
        mc.setBlock( loc.x-x, loc.y, loc.z-z, magic_block(block_type))
        mc.setBlock( loc.x+z, loc.y, loc.z+x, magic_block(block_type))
        mc.setBlock( loc.x-z, loc.y, loc.z+x, magic_block(block_type))
        mc.setBlock( loc.x+z, loc.y, loc.z-x, magic_block(block_type))
        mc.setBlock( loc.x-z, loc.y, loc.z-x, magic_block(block_type))

def make_bubble(mc, loc, radius, block_type=None):
    # Define a bunch of concentric circles with different radii. Sort of like
    # cutting a tomato. These circles are stacked along the z-axis and there are
    # 2*r of them.
    for subr in range(int(radius)):
        ring_radius = math.sqrt(radius**2 - (subr+0.5)**2)
        make_xy_ring(mc, loc+Vec3(0,0,subr), ring_radius, block_type)
        make_xy_ring(mc, loc+Vec3(0,0,-subr), ring_radius, block_type)
        make_xz_ring(mc, loc+Vec3(0,subr,0), ring_radius, block_type)
        make_xz_ring(mc, loc+Vec3(0,-subr,0), ring_radius, block_type)

class mock_mc(object):
    def setBlock(self, x,y,z, block_type):
        print x,y,z, "=" + str(block_type)
    def setBlocks(self, x1,y1,z1, x2,y2,z2, block_type):
        print x1,y1,z1, x2,y2,z2, "=" + str(block_type)

def make_wall(mc, x,y,z, length, direction, block_type):
    for i in range(length):
        x1 = x
        y1 = y
        z1 = z

        if direction == 0: x1 += i
        if direction == 1: z1 += i
        if direction == 2: x1 -= i
        if direction == 3: z1 -= i

        ys = []
        for x0 in range(x1-1, x1+2):
            for z0 in range(z1-1, z1+2):
                ys.append(mc.getHeight(x0,z0))
        y1 = ys[4] # Pick the middle height
        y2 = max(ys) + 1
        mc.setBlocks(x1,y1,z1, x1, y2, z1, block_type)

def clear_material(mc, x1,y1,z1, x2,y2,z2, block_type):
    for x in range(x1,x2+1):
        for y in range(y1,y2+1):
            for z in range(z1,z2+1):
                if mc.getBlockWithData(x,y,z) == block_type:
                    mc.setBlock(x,y,z, block.AIR)


# directions: '+x', '-x', '+y', '-y'
def find_path(x1,z1,x2,z2):
    cx = x1
    cz = z1
    dirs = []
    while cx != x2 and cz != z2:
        if cx < x2:
            dirs.append('+x')
            cx = cx + 1
        elif cx > x2:
            dirs.append('-x')
            cx = cx - 1

        if cz < z2:
            dirs.append('+z')
            cz = cz + 1
        elif cz > z2:
            dirs.append('-z')
            cz = cz - 1

    return dirs

# return an array of x,z coords starting at x,z and following path.
def walk_path(x, z, path):
    yield x, z
    for d in path:
        if d == '+x':
            x = x + 1
        elif d == '-x':
            x = x - 1
        elif d == '+z':
            z = z + 1
        elif d == '-z':
            z = z - 1
        else:
            print "I can't read your direction:", d
        yield x, z

# Walk along a path setting block_type at every point.
def mark_path(mc, x,z, path, block_type):
    for x, z in walk_path(x,z,path):
        mc.setBlock(x,mc.getHeight(x,z),z, block_type)


if __name__ == "__main__":
    mc = minecraft.Minecraft.create("mcpi.mooo.com")
    loc = Vec3(-195,10,40)
    mc.setBlocks(
        loc.x-5, loc.y   , loc.z-5,
        loc.x+5, loc.y+30, loc.z+5,
        block.AIR)
    grow_tree(mc, loc)
