from sympy import Symbol, I, Integer, AtomicExpr, Rational, latex, Number, Expr, symbols, simplify
import numbers
MAX_DEGREE = 4

def set_max_degree(max_degree: int):
    MAX_DEGREE=max_degree

class DifferentialForm():
    def __init__(self,symbol,degree=0, exact=False):
        """
        Class: Differential Form

        This is the basic class of this package. It holds all the information needed for a generic differential form.
        
        """
        self.degree = degree
        self.symbol = symbol
        self.exact = exact
        if degree < 0 or degree > MAX_DEGREE:
            self.symbol = Number(0)
        
    # def __new__(self,symbol,degree=0):
    #     # return super().__new__(cls,*args,**kwargs)
    #     return self

    def __mul__(self,other):
        if isinstance(other,AtomicExpr):
            return DifferentialFormMul(self,other)
        elif isinstance(other,Expr):
            return DifferentialFormMul(self,other)
        elif isinstance(other,int):
            return DifferentialFormMul(self,Integer(other))
        elif isinstance(other,float):
            return DifferentialFormMul(self,Rational(other))
        elif isinstance(other,DifferentialForm):
            ret = DifferentialFormMul()
            ret.forms_list = [[self,other]]
            ret.factors = [1]
            return ret
        elif isinstance(other,DifferentialFormMul):
            return DifferentialFormMul(self,1)*other
        else:
            raise NotImplementedError("Not implemented multiplication of type '"+str(type(self).__name__)+" * "+str(type(other).__name__)+"'")
    
    def __add__(self,other):
        ret = DifferentialFormMul()
        if isinstance(other,AtomicExpr):
            ret.forms_list = [[self],[DifferentialForm(Integer(1),0)]]
            ret.factors = [1,other]
        elif isinstance(other,Expr):
            ret.forms_list = [[self],[DifferentialForm(Integer(1),0)]]
            ret.factors = [1,other]
        elif isinstance(other,int):
            ret.forms_list = [[self],[DifferentialForm(Integer(1),0)]]
            ret.factors = [1,other]
        elif isinstance(other,float):
            ret.forms_list = [[self],[DifferentialForm(Integer(1),0)]]
            ret.factors = [1,other]
        elif isinstance(other,DifferentialForm):
            ret.forms_list = [[self],[other]]
            ret.factors = [1,1]
        elif isinstance(other,DifferentialFormMul):
            ret.forms_list = [[self]]+other.forms_list
            ret.factors = [1]+other.factors
        else:
            raise NotImplementedError
        return ret
    
    def __lt__(self,other):
        if not isinstance(other,DifferentialForm): raise NotImplementedError
        if str(self.symbol) < str(other.symbol):
            return True
        elif str(self.symbol) > str(other.symbol):
            return False
        else:
            return (self.degree) < other.degree

    def __neg__(self): return DifferentialFormMul(self,-1)
    def __sub__(self,other): return self + (-other)
    def __rsub__(self,other): return (-self) + other
    def __radd__(self,other): return self + other
    def __rmul__(self,other): return self * other

    def __str__(self):
        return latex(self.symbol)

    def __repr__(self):
        return self.symbol._repr_latex_()

    def _repr_latex_(self):
        return self.symbol._repr_latex_()

    def _latex(self,printer):
        return self._repr_latex_()
    
    def _print(self):
        return self._repr_latex_()
    
    def __eq__(self,other):
        if isinstance(other,DifferentialForm):
            return str(self.symbol) == str(other.symbol) and self.degree == other.degree
    
    @property
    def d(self):
        if self.exact: return DifferentialForm(Number(0),self.degree+1,exact=True)
        elif isinstance(self.symbol,Number): return DifferentialForm(Number(0),self.degree+1,exact=True)
        else:
            dsymbol = symbols("d"+str(self.symbol))
            return DifferentialForm(dsymbol,degree=self.degree+1,exact=True)
        raise NotImplementedError
    
    def simplify(self):
        return self


class DifferentialFormMul():
    def __init__(self,form:DifferentialForm=None,factor:AtomicExpr=None):
        if form == None:
            self.forms_list = []
            self.factors = []
        else:
            self.forms_list = [[form]]
            self.factors = [factor]

    
    def __add__(self,other):
        ret = DifferentialFormMul()
        if isinstance(other,DifferentialFormMul):
            ret.forms_list += (self.forms_list)
            ret.forms_list += (other.forms_list)
            ret.factors += self.factors + other.factors

            ret.__sort_form_sums()
            ret.__collect_forms()
            return ret
        elif isinstance(other,DifferentialForm):
            ret.forms_list += self.forms_list
            ret.factors += self.factors
            if isinstance(other.symbol,Number):
                ret.forms_list += [[DifferentialForm(Number(1),0,exact=True)]]
                ret.factors += [other.symbol]
            elif isinstance(other.symbol,Expr):
                ret.forms_list += [[DifferentialForm(Number(1),0,exact=True)]]
                ret.factors += [other.symbol]
            elif isinstance(other.symbol,AtomicExpr):
                ret.forms_list += [[DifferentialForm(Number(1),0,exact=True)]]
                ret.factors += [other.symbol]
            else:
                ret.forms_list += [[other]]
                ret.factors += [1]
            ret.__collect_forms()
            return ret
        elif isinstance(other,int):
            return self + DifferentialForm(Integer(other),0)
        elif isinstance(other,float):
            return self + DifferentialForm(Rational(other),0)
        elif isinstance(other,AtomicExpr):
            return self + DifferentialForm(other,0)
        elif isinstance(other,Expr):
            return self + DifferentialForm(other,0)
        else:
            raise NotImplementedError
    
    def __mul__(self,other):
        ret = DifferentialFormMul()
        if isinstance(other,int):
            ret.forms_list = self.forms_list
            ret.factors = [Integer(other)*f for f in self.factors]

        elif isinstance(other,float):
            ret.forms_list = self.forms_list
            ret.factors = [Rational(other)*f for f in self.factors]

        elif isinstance(other,AtomicExpr):
            ret.forms_list = self.forms_list
            ret.factors = [(other)*f for f in self.factors]

        elif isinstance(other,Expr):
            ret.forms_list = self.forms_list
            ret.factors = [(other)*f for f in self.factors]            

        elif isinstance(other,DifferentialForm):
            ret.forms_list = [fl+[other] for fl in self.forms_list]
            ret.factors = self.factors

            ret.__remove_squares()
            ret.__remove_above_top()
            ret.__sort_form_sums()
            ret.__collect_forms()
        
        elif isinstance(other,DifferentialFormMul):
            for i in range(len(self.forms_list)):
                for j in range(len(other.forms_list)):
                    ret.forms_list.append(self.forms_list[i]+other.forms_list[j])
                    ret.factors.append(self.factors[i]*other.factors[j])

            ret.__remove_squares()
            ret.__remove_above_top()
            ret.__sort_form_sums()
            ret.__collect_forms()
        else:
            raise NotImplementedError
        
        ret.__remove_squares()
        ret.__remove_above_top()
        ret.__sort_form_sums()
        ret.__collect_forms()

        return ret
    
    def __rmul__(self,other):
        ret = DifferentialFormMul()
        if isinstance(other,int):
            ret.forms_list = self.forms_list
            ret.factors = [Integer(other)*f for f in self.factors]

        elif isinstance(other,float):
            ret.forms_list = self.forms_list
            ret.factors = [Rational(other)*f for f in self.factors]

        elif isinstance(other,AtomicExpr):
            ret.forms_list = self.forms_list
            ret.factors = [(other)*f for f in self.factors]

        elif isinstance(other,Expr):
            ret.forms_list = self.forms_list
            ret.factors = [(other)*f for f in self.factors]            

        elif isinstance(other,DifferentialForm):
            ret.forms_list = [[other]+fl for fl in self.forms_list]
            ret.factors = self.factors

            ret.__remove_squares()
            ret.__remove_above_top()
            ret.__sort_form_sums()
            ret.__collect_forms()
        elif isinstance(other,DifferentialFormMul):
            for i in range(len(self.forms_list)):
                for j in range(len(other.forms_list)):
                    ret.forms_list.append(other.forms_list[j]+self.forms_list[i])
                    ret.factors.append(self.factors[i]*other.factors[j])

            ret.__remove_squares()
            ret.__remove_above_top()
            ret.__sort_form_sums()
            ret.__collect_forms()
        else:
            raise NotImplementedError
        
            ret.__remove_squares()
            ret.__remove_above_top()
            ret.__sort_form_sums()
            ret.__collect_forms()
        return ret

    def __radd__(self,other): return self + other
    def __neg__(self):
        ret = DifferentialFormMul()
        ret.forms_list = self.forms_list
        ret.factors = [-f for f in self.factors]
        return ret
    
    def __sub__(self,other): return self + (-other)
    def __rsub__(self,other): return other + (-self)

    def __remove_squares(self):
        i = 0
        while i < len(self.forms_list):
            deled = False
            for j in range(len(self.forms_list[i])):
                if self.forms_list[i][j].degree %2 == 1:
                    if len([k for k,e in enumerate(self.forms_list[i]) if e == self.forms_list[i][j]]) > 1:
                        del self.forms_list[i]
                        del self.factors[i]
                        deled = True
                        break
            if not deled: i+=1
        
    def __remove_above_top(self):
        i = 0
        while i < len(self.forms_list):
            if sum([f.degree for f in self.forms_list[i]]) > MAX_DEGREE:
                del self.forms_list[i]
                del self.factors[i]
                continue
            i += 1

    def __sort_form_sums(self):
        for i in range(len(self.forms_list)):
            bubble_factor = 1
            for j in range(len(self.forms_list[i])):
                for k in range(j,len(self.forms_list[i])):
                    if self.forms_list[i][j] < self.forms_list[i][k]:
                        temp = self.forms_list[i][j]
                        self.forms_list[i][j] = self.forms_list[i][k]
                        self.forms_list[i][k] = temp
                        bubble_factor *= (-1)**(self.forms_list[i][j].degree*self.forms_list[i][k].degree)
            self.factors[i] = self.factors[i]*bubble_factor
    
    def __collect_forms(self):
        new_forms_list = []
        new_factors = []
        for i in range(len(self.forms_list)):
            if self.forms_list[i] not in new_forms_list:
                new_forms_list.append(self.forms_list[i])
                new_factors.append(self.factors[i])
            else:
                j = new_forms_list.index(self.forms_list[i])
                new_factors[j] += self.factors[i]
        
        i = 0
        while  i < len(new_forms_list):
            if new_factors[i] == 0:
                del new_factors[i]
                del new_forms_list[i]
                continue
            i+=1
    
        i = 0
        while i < len(new_forms_list):
            new_forms_strings = [str(f) for f in new_forms_list[i]]
            if '0' in new_forms_strings:
                del new_forms_list[i]
                del new_factors[i]
                continue
            if len(new_forms_list[i]) > 1 and '1' in new_forms_strings:
                new_forms_list[i].pop(new_forms_strings.index('1'))
            i+=1




        self.forms_list = new_forms_list
        self.factors = new_factors
            
    def _repr_latex_(self):
        latex_str = "$" + "+".join([ "(" + latex(self.factors[i]) + ")" + r" \wedge ".join([str(f) for f in self.forms_list[i]]) for i in range(len(self.forms_list))]) + "$"
        if latex_str == "$$":
            return "$0$"
        return latex_str
    
    @property
    def d(self):
        ret = DifferentialFormMul()
        new_forms_list = []
        new_factors_list = []
        for i in range(len(self.forms_list)):
            fact = self.factors[i]
            for f in fact.free_symbols:
                dfact = fact.diff(f)
                if dfact != 0:
                    new_forms_list += [[DifferentialForm(f,0).d] + self.forms_list[i]]
                    new_factors_list += [dfact]
            for j in range(len(self.forms_list[i])):
                d_factor = (-1)**sum([0] + [f.degree for f in self.forms_list[i][0:j]])
                new_forms_list += [self.forms_list[i][0:j] + [self.forms_list[i][j].d] + self.forms_list[i][j+1:]]
                new_factors_list += [d_factor*self.factors[i]]

        ret.forms_list = new_forms_list
        ret.factors = new_factors_list

        ret.__remove_squares()
        ret.__remove_above_top()
        ret.__sort_form_sums()
        ret.__collect_forms()

        return ret

    def simplify(self):
        ret = DifferentialFormMul()
        ret.forms_list = self.forms_list.copy()
        ret.factors = []
        for i in range(len(self.factors)):
            ret.factors.append(simplify(self.factors[i]))

        return ret
    
def d(form):
    if isinstance(form,DifferentialForm) or isinstance(form,DifferentialFormMul):
        return form.d
    elif isinstance(form,Expr):
        ret = DifferentialFormMul()
        new_forms_list = []
        new_factors_list = []
        for f in form.free_symbols:
            dform = form.diff(f)
            if dform != 0:
                new_forms_list += [[DifferentialForm(f,0).d]]
                new_factors_list += [dform]
        
        ret.forms_list = new_forms_list
        ret.factors = new_factors_list
        return ret
    elif isinstance(form,numbers.Number):
        return 0
    raise NotImplementedError


        
    