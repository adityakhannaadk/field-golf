import math
# tss is the timestep dt 
# softening factor eps
# you can basically think of this as the distance between the screen on which the test charge is shuttling about and all the other charges
# this basically satisfies the purpose that we dont want charges to get too close to each other
# however if its too high it results in rosette orbits

class verlet:
    # this could v much be optimised
    # i could turn everything into just vectors and stuff but i honestly cannot be arsed to change it now
    # i made it like this from the beginning and now i cba fix it


    def __init__(self, eps: float, tss: float) -> None:
        self.eps = eps
        self.tss = tss
        self.qB = 1000
        self.kqQ_nsign = 100000
        self.iscurrinbfield = False
        self.no_charges = False
        self.velo_y = 0
        self.velo_x = 0
        self.position = [0, 0]  # Add this to keep track of current position


    def get_r(self, x, y, electronx, electrony):
        return math.sqrt((electronx - x) ** 2 + (electrony - y) ** 2 + self.eps)
    
    def electron_acc_x(self, x, y, electronx, electrony, sgn):
        r = self.get_r(x, y, electronx, electrony)
        kqQ = sgn * self.kqQ_nsign
        adjacent = electronx - x

        acc = (kqQ / (r ** 3)) * adjacent
        if self.iscurrinbfield:
            acc += self.qB * self.velo_y / r  # Normalize by r to make force proportional to velocity
        return acc

    def electron_acc_y(self, x, y, electronx, electrony, sgn):
        r = self.get_r(x, y, electronx, electrony)
        kqQ = sgn * self.kqQ_nsign
        opposite = electrony - y
        acc = (kqQ / (r ** 3)) * opposite
        if self.iscurrinbfield:
            acc -= self.qB * self.velo_x / r  # Normalize by r to make force proportional to velocity
        return acc

    def accn_dpx(self, x, y, ecoords):
        net_acc = 0
        if self.iscurrinbfield and ecoords == []:
            return self.qB * self.velo_y
        for m in ecoords:
            net_acc += self.electron_acc_x(x, y, m[0], m[1], m[2])
        return net_acc

    def accn_dpy(self, x, y, ecoords):
        net_acc = 0
        if self.iscurrinbfield and ecoords == []:
            return -self.qB * self.velo_x
        for m in ecoords:
            net_acc += self.electron_acc_y(x, y, m[0], m[1], m[2])
        return net_acc

    # 4th order Runge Kutta sim
    def ts_x(self, pvx, pvy, ecoords, Bfield=False):
        self.iscurrinbfield = Bfield
        self.position[0] = pvx[0]
        self.position[1] = pvy[0]
        self.velo_x = pvx[1]
        self.velo_y = pvy[1]

        x, x1 = pvx[0], pvx[1]
        h = self.tss
        k1 = h * x1
        # first step, simply the stepsize * previous velocity 
        # i.e. dx/dt*dt 
        k2 = h * (x1 + 0.5 * h * self.accn_dpx(x, pvy[0], ecoords))
        # middle step, now considering the accn at that point 
        # i.e. dt*(dx/dt + 0.5*dt*d^2x/dt^2)
        k3 = h * (x1 + 0.5 * h * self.accn_dpx(x + 0.5 * h, pvy[0],ecoords))
        # middle step, now considering the accn at a point displaced by 0.5*stepsize
        k4 = h * (x1 + h * self.accn_dpx(x + h, pvy[0], ecoords))
        x += (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        x1 += h * self.accn_dpx(x, pvy[0], ecoords)
        return [x, x1]

    def ts_y(self,pvx, pvy, ecoords):

        y, y1 = pvy[0], pvy[1]
        h = self.tss
        k1 = h * y1
        k2 = h * (y1 + 0.5 * h * self.accn_dpy(pvx[0], y, ecoords))
        k3 = h * (y1 + 0.5 * h * self.accn_dpy(pvx[0], y + 0.5 * h, ecoords))
        k4 = h * (y1 + h * self.accn_dpy(pvx[0], y + h, ecoords))
        y += (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        y1 += h * self.accn_dpy(pvx[0], y, ecoords)
        return [y, y1]
    

    # using verlet integration instead
    def ts_x_verlet(self,pvx, pvy, ecoords, Bfield=False):
        print(f"Before setting, iscurrinbfield: {self.iscurrinbfield}")
        self.iscurrinbfield = Bfield
        print(f"After setting, iscurrinbfield: {self.iscurrinbfield}")
        # get curr posn and velo 
        x, x1 = pvx[0], pvx[1]
        
        # delta t
        h = self.tss
        
        # accn along x 
        ax = self.accn_dpx(x, pvy[0], ecoords)
        
        # update x position using kinematic equation (x0 + delta_t*(dx/dt) + 1/2*(d2x/dt2)*(delta_t^2)
        x_new = x + x1 * h + 0.5 * ax * h**2
        
        # new accn 
        ax_new = self.accn_dpx(x_new, pvy[0], ecoords)
        
        # velo update v = u + (a_old + a_new)/2*delta_t
        x1_new = x1 + 0.5 * (ax + ax_new) * h
        self.velo_x = x1_new
        # ret
        return [x_new, x1_new]

    def ts_y_verlet(self,pvx, pvy, ecoords):
        y, y1 = pvy[0], pvy[1]
        h = self.tss
        ay = self.accn_dpy(pvx[0], y, ecoords)
        y_new = y + y1 * h + 0.5 * ay * h**2
        ay_new = self.accn_dpy(pvx[0], y_new, ecoords)
        y1_new = y1 + 0.5 * (ay + ay_new) * h
        self.velo_y = y1_new
        return [y_new, y1_new]