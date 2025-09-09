"""
Created on Mon Sep  8 13:39:33 2025

@author: brad
Massive thanks to Nayan Dusoruth for the bulk of this code and support in writing it
https://github.com/NayanDusoruth
"""
import sympy as sy
import numpy as np
import pandas as pd

def expressionSum(expressions):
    """Utility function to take the sum of multiple sympy expressions"""
    sm = 0
    for i in expressions:
        sm += i
    return sm

def errorPropTerm(expression, variable):
    """Takes the partial derivative of the input expression to produce the error propagation term"""
    errorVariable = sy.symbols(f"{variable}_err")
    return (errorVariable * expression.diff(variable))**2, errorVariable

def errorPropagate(expression, returnSymbols = False):
    """Calculates the error propagation term for all free symbols in an expression"""
    symbols = list(expression.free_symbols)
    
    expressions = []
    errorSymbols = []
    
    # Looping through all symbols and finding their respective error term
    for symbol in symbols:
        errorTerm, errorVariable = errorPropTerm(expression, symbol)
        expressions.append(errorTerm)
        errorSymbols.append(errorVariable)
    
    if returnSymbols:
        return expressions, symbols+errorSymbols
    
    return expressions

def errorPropEqs(equation, returnSummation=False, returnSummationSqrt = False):
    """Finds the error propagation equation for a given input equation"""
    errorTerms, symbols = errorPropagate(equation.rhs, returnSymbols = True)
    
    equations = []
    LHSsymbols = []
    for i in range(len(errorTerms)):
        LHSterm = sy.symbols(f"{list(equation.lhs.free_symbols)[0]}_{symbols[i]}_err")**2
        LHSsymbols.append(LHSterm)
        equations.append(sy.Eq(LHSterm, errorTerms[i]))
    
    if returnSummation:
        LHSsummation = sy.symbols(f"{equation.lhs}_err")**2
        summationEq = sy.Eq(LHSsummation, expressionSum(LHSsymbols,))
        return equations, summationEq
    
    if returnSummationSqrt:
        LHSsummation = sy.symbols(f"{equation.lhs}_err")
        summationEq = sy.Eq(LHSsummation, sy.sqrt(expressionSum(LHSsymbols)))
        return equations, summationEq
    
    return equations

def evalEquation(equation, inputs, evalNumeric=False):
    """Evaluates a given equation by plugging in inputs"""
    rhs = equation.rhs
    lhsSymbol = equation.lhs
    
    for symbol, value in inputs.items():
        rhs = rhs.subs(symbol, value)
        
    if evalNumeric:
        rhs.evalf()
    
    return {lhsSymbol:rhs}


class multipleEquations():
    """"""
    def __init__(self, equations, constants={}, propagate=True, freeVars = True):
        self.equations = equations
        self.constants = constants
        
        if propagate:
            self.errorPropagation()
        if freeVars:
            self.freeVars()
        
    def freeVars(self):
        """Pulls all free variables from the input equations"""
        rhsVariables = np.array([])
        fixedVariables = np.array([])
        indices = np.array([])
        
        for equation in self.equations:
            rhsVariables = np.append(rhsVariables, list(equation.rhs.free_symbols))
            fixedVariables = np.append(fixedVariables, list(equation.lhs.free_symbols))
        
        fixedVariables = np.append(fixedVariables, list(self.constants.keys()))
        
        for symbol in fixedVariables:
            indices = np.append(indices, np.where(rhsVariables == symbol))
        indices = indices.astype(int)
        
        if len(indices) != 0:
            self.freeVariables = np.delete(rhsVariables, indices)
        
    def errorPropagation(self):
        """Finds the error propagation expression for the input equations"""
        errorTerms = []
        
        for equation in self.equations:
            errorEquations, summation = errorPropEqs(equation, returnSummationSqrt = True)
            errorTerms = np.append(errorTerms, errorEquations)
            errorTerms = np.append(errorTerms, summation)
            
        self.equations = np.append(self.equations, errorTerms)
        
    def evalEquations(self, inputs):
        """Evaluates all input equations based on inputs"""
        values = inputs
        values.update(self.constants)
        
        for equation in self.equations:
            values.update(evalEquation(equation, values))
        
        return values
    
    def bulkEvalEquations(self, inputs):
        """Evaluates all input equations with multiple inputs"""
        outputs = np.array([])
        
        for i in range(0, inputs.shape[0]):
            outputs = np.append(outputs, self.evalEquations(inputs.iloc[1].to_dict()))
        
        return pd.DataFrame.from_dict(outputs.tolist())
    
    def texPrint(self):
        
        for equation in self.equations:
            print(f"{sy.latex(equation)}\n")
            
    def pyPrint(self):
        
        functions = ["sin", "cos", "tan", "sqrt", "asin", "acos", "atan", "exp"]
        
        for equation in self.equations:
            equation = str(equation)
            
            for function in functions:
                if equation.find(function) != -1:
                    equation = equation.replace(function, f"np.{function}")
            
            print(f"{equation}\n")
    
    def prettyPrint(self):
        
        for equation in self.equations:
            sy.pprint(equation)
            print("\n")


