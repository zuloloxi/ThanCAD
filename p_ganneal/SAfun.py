###############################################################################
# ntualinprog 1.0.1 "Students2021": optimization tools for GNU Octave
#
# Copyright (C) 2021-2022 Thanasis Stamos, January 18, 2022
# Athens, Greece, Europe
# URL: http://thancad.sourceforge.net
# e-mail: cyberthanasis@gmx.net
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details (www.gnu.org/licenses/gpl.html).
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###############################################################################

class SAfun(SAAnnealable):
    "Find the minimum of an arbitrary function of n dimensions."
    properties
        fun
        nvars
        A
        b
        Aeq
        beq
        lb
        ub
        nonlcon
        intcon
        deltax
        istep
        state
        bmin
        beqmin
        beqmax
        c
        cmin
        ceq
        ceqmin
        ceqmax
        randb
        randib
    end

    def __init__(self, fun, nvars, A=None, b=None, Aeq=None, beq=None, lb=None, ub=None, nonlcon=None, intcon=()):
        super().__init__()    #base constructor automatically called (without input arguments)
        self.checkargs(fun, nvars, A, b, Aeq, beq, lb, ub, nonlcon, intcon)
        self.fun = fun
        self.nvars = nvars
        self.A = np.array(A)
        self.b = np.array(b)
        self.Aeq = np.array(Aeq)
        self.beq = np.array(beq)
        self.lb = np.array(lb)
        self.ub = np.array(ub)
        self.nonlcon = nonlcon
        self.intcon = intcon

        self.randb = lambda lb, ub: np.rand(size(lb)).*(ub-lb) + lb     #Real valued random numbers between lb and ub.
        self.randib = lambda lb, ub: int(np.rand(size(lb)).*(ub-lb+1)) + lb   #Integer valued random numbers between lb and ub.

        self.istep = 0;   #istep is zero until the end of initState()
        self.deltax = self.ub-self.lb
        self.bmin = np.array(b)
        self.beqmin = np.array(beq)
        self.beqmax = np.array(beq)

        intconx = []
        for i in range(nvars):
            if i in intcon: continue
            intconx.append(i)  #real valued variable

        #self.state.x = rand(nvars, 1).*(self.ub-self.lb) + self.lb;
        self.state = p_ggen.Struct()
        self.state.x = np.zeros((nvars,)
        self.state.x[intconx] = self.randb(self.lb[intconx], self.ub[intconx])
        self.state.x[intcon]  = self.randib(self.lb[intcon], self.ub[intcon])
    #end %function

    def checkargs(self, fun, nvars, A, b, Aeq, beq, lb, ub, nonlcon, intcon)
        def checkA(A, b, suf):
            #Check matrices A and b, or Aeq, and beq
            if A:
                if np.size(A,2 ) != nvars:
                    raise ValueError('The number of columns of A%s do not agree with nvars' % (suf,))
            if b && np.size(b, 2) ~= 1
                reaise ValueError('b%s must be a column vector' % (suf,))
            if np.size(A, 1) != np.size(b, 1):
                raise ValueError('The number of rows of A%s and b%s must be the same' % (suf, suf))

        if not iscallable(fun):
            raise ValueError('Invalid fun value: should be function/callable')
        if nonlcon is not None:
            if not iscallable(nonlcon)
                raise ValueError('Invalid nonlcon value: should be function/callable')
        if nvars < 1 or nvars ~= round(nvars)
            raise ValueError('Invalid nvars value')
        #if np.size(lb, 2) ~= 1 || np.size(ub, 2) ~= 1
        #    raise ValueError('lb and ub must be column vectors');
        if size(lb, 1) != nvars or size(ub, 1) != nvars:
            raise ValueError('lb and/or ub dimensions do not agree with nvars');
        end
        if any(lb >= ub): raise ValueError('safun(): lb should be: lb < ub for all variables')
        checkA(A, b, '');
        checkA(Aeq, beq, 'eq');
        if len(intcon) > 1
            if size(intcon, 2) ~= 1
                error('intcon should be a column vector');
            end
            if any(intcon ~= round(intcon)) || any(intcon < 1) || any(intcon > nvars)
                error('invalid intcon values');
            end
            for j=1:length(intcon)-1
                if any(intcon(j) == intcon(j+1:end))
                    error('duplicate values in intcon')
                end
            end
            if any(lb(intcon) ~= round(lb(intcon))) || any(ub(intcon) ~= round(ub(intcon))) 
                error('lb and ub bounds of integer variables should be integer');
            end
        end
    end %function


    function analenergy(self)
        %It is called after every temperature step; gradually decrease the maximum change in changeState().
        self.istep = self.istep + 1;
        k = min(self.istep+1, 20);
        self.deltax = (self.ub-self.lb) ./ k;
        self.deltax(self.intcon) = max(round(self.deltax(self.intcon)), 1);
    end


    function n=getDimensions(self)
        %"Return the dimensionality of current configuration of the annealing object."
        n=self.nvars;
    end


    function e=energy(self)
        %"Return the energy of the current configuration - without penalties."
        e = self.fun(self.state.x);
        if isempty(self.emin) || e < self.emin   %emin and emax contain no penalty
            self.emin = e;
        end
        if isempty(self.emax) || e > self.emax
            self.emax = e;
        end
    end


    function e=energyState(self)
        %"Return the energy of the current configuration."
        e = self.energy();
        per=self.getViolation();
        penalty = (self.emax-self.emin).*per;
        e = e + penalty;
    end %function


    function per=getViolation(self)
        %Find biggest violation as a percentage
        [bcur, beqcur, ccur, ceqcur] = self.constraintsmin();   %Find min and max values of energy and constraints
        %Find biggest non compliance
        per = 0;   %percentage of exceedence
        per = self.penalty(per, bcur, self.b, self.bmin, beqcur, self.beq, self.beqmin, self.beqmax);
        per = self.penalty(per, ccur, self.c, self.cmin, ceqcur, self.ceq, self.ceqmin, self.ceqmax);
    end


    function per = penalty(self, per, bcur, b, bmin, beqcur, beq, beqmin, beqmax)
        %Find biggest non compliance
        if ~isempty(bcur)
            deps =1e-10;  %if less than that, the difference is considered as zero
            db = b-bmin;
            if any(db<deps)
                db1 = mean(db);
                if db1 < deps; db1 = 1.0; end   %Arbitrarily set the difference=1.0
                db(db<deps) = db1;    %if self.b==self.bmin, set the difference to average dif, or 1.0
            end
            per1 = max((bcur - b)./db);
            per = max(per, per1);
        end
        if ~isempty(beqcur)
            deps =1e-10;  %if less than that, the difference is considered as zero
            db = beqmax-beqmin;
            if any(db<deps)
                db1 = mean(db);
                if db1 < deps; db1 = 1.0; end   %Arbitrarily set the difference=1.0
                db(db<deps) = db1;    %if self.b==self.bmin, set the difference to average dif, or 1.0
            end
            per1 = max(abs(beqcur - beq)./db);
            per = max(per, per1);
        end
    end

    function state=getState(self)
        %"Return an object which fully reflects the state of the annealing object."
        %state = struct();
        state = self.state;
    end

    function setState(self, state)
        %"Replace current state of the annealing object with the one in variable state."
        self.state = state;
    end

    function changeState(self)
        %Randomly change the configuration of the problem.
        %changestate should not save current configuration before changing the
        %state (anneal() does this automatically).
        n = self.nvars;
        k = randi(n);
        randx = self.randb;
        if any(k==self.intcon); randx = self.randib; end
        if self.istep == 0
            self.state.x(k) = randx(self.lb(k), self.ub(k));
        else
            while true
                temp = self.state.x(k) + randx(-self.deltax(k), self.deltax(k));
                if temp >= self.lb(k) && temp <= self.ub(k); break; end
            end
            self.state.x(k) = temp;
        end
    end


    function ok=initState(self, tempr, spSch)
        %Initialize random changes and calibrate energy.
        %We assume that the configuration is valid, perhaps through
        %__init__() or some other function which has already been called.
        self.efact = 1.0;
        ndim = self.getDimensions();  % Dimension is fixed in this problem
        ntries = ndim*spSch;
        for i=1:ntries              % Now, randomize a bit
            self.changeState();
            e = self.energy();      %Find min and max values of energy
            [bcur, beqcur, ccur, ceqcur] = self.constraintsmin();   %Find min and max values of energy and constraints
        end
        e1 = self.energyState();               % Initial energy %Thanasis2011_05_19:This is NOT multiplied by efact
        de = 0.0;
        ntries = ndim*spSch;
        npos = 0;
        ok = false;
        for j=1:5
            for i=1:ntries
                self.changeState();
                e2 = self.energyState();       %Thanasis2011_05_19:This is NOT multiplied by efact
                if e2 > e1
                    de = de + e2-e1;
                    npos = npos + 1;
                end
                e1 = e2;
            end
            %fprintf('==============================================================================\n');
            %fprintf('npos=%d ntries=%d j=%d\n', npos, ntries,  j);
            %fprintf('==============================================================================\n');
            if npos > ntries/2; ok=true; break; end
        end
        if ~ok; return; end                  % Could not do calibration
        de = de / npos;
        self.efact = tempr / de;             % Normalise delta energy to tempr (=100): efact*de = tempr
        %self.prt(sprintf('Αρχική ενέργεια=%.3f', e1);
        %self.prt(sprintf('Αρχική μέση Δε =%.3f', de);
        %fprintf('Minimum energy=%.3f\n', self.emin);
        %fprintf('Maximum energy=%.3f\n', self.emax);
    end %function

    function [bcur, beqcur, ccur, ceqcur]=constraintsmin(self)
        %Find min of contraints
        bcur = [];
        beqcur = [];
        ccur = [];
        ceqcur = [];
        if ~isempty(self.A)
            bcur = self.A * self.state.x;
            self.bmin = min(self.bmin, bcur);  %Note that self.bmin is not empty
        end
        if ~isempty(self.Aeq)
            beqcur = self.Aeq * self.state.x;
            self.beqmin = min(self.beqmin, beqcur);  %Note that self.beqmin is not empty
            self.beqmax = max(self.beqmax, beqcur);  %Note that self.beqmax is not empty
        end
        if ~isempty(self.nonlcon)
            [ccur, ceqcur] = self.nonlcon(self.state.x);
            if isempty(self.c)
                self.c = zeros(size(ccur));   %This is cmax (zero)
                self.cmin = ccur;
                self.ceq = zeros(size(ceqcur));   %This is ceq (zero)
                self.ceqmin = ceqcur;
                self.ceqmax = ceqcur;
            else
                if any(size(ccur)~=size(self.cmin))
                    error('The size of vector c must be consistent at every call to nonlcon');
                end
                self.cmin = min(self.cmin, ccur);
                if any(size(ceqcur)~=size(self.ceqmin))
                    error('The size of vector ceq must be consistent at every call to nonlcon');
                end
                self.ceqmin = min(self.ceqmin, ceqcur);
                self.ceqmax = max(self.ceqmax, ceqcur);
            end
        end
    end %function

    end %methods

end %classdef
