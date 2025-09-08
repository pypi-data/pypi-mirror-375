from scipy.optimize import minimize
import numpy as np
from .chi_calculator import ChiCalculator

class StressStrain():
    """
    Class for fitting model parameters to stress-strain data.
    Currently, this only works if sitting the *instantaneous*
    stress-strain respose.
    """

    def __init__(self, axial_data):
        """
        Constructor.  The data should be a dict of dicts,
        where the primary keys are labels for the data/model
        and the primary values is a dictionary that contains
        the data and the model.  The data should consist of the:

        - axial strain (units of mm/mm, positive for tension)
        - axial stress (units of Pa, positive for tension)
        - the model to use for that particular data
        """

        self.data = axial_data
        self.strain_to_stretch()

    def strain_to_stretch(self):
        """
        Converts strain data (mm/mm) into stretch (lambda_z)
        data.  Assumes that tensile strains are positive 
        and compressive strains are negative.
        """

        for label in self.data:
            strain_data = self.data[label]["strain_data"]
            self.data[label]["stretch_data"] = 1 + strain_data

    def solve(self, fitting_params, normalisation_factors = None, fixed_hydration = False):
        """
        Carries out the minimisation using SciPy's solvers

        Inputs: 
        
        fitting_params = a dictionary where the keys are strings
        that describe the parameters to fit and the values are
        initial guess.  
        
        normalisation_factors = an optional list of numerical values that
        can be used to normalise the parameters to improve the performance
        of the optimiser

        fixed_hydration = a flag that determines whether the initial
        hydration of the material should be kept constant during the
        fit

        Outputs:

        fitted_vals = a NumPy array with values of the fitted 
        """

        print('----------------------')
        print(f'Stress-strain fit')

        # build the initial condition array
        X_0 = list(fitting_params.values())
        
        if normalisation_factors is None:
            normalisation_factors = len(X_0) * [1]        
        
        # normalise the initial guess
        for n in range(len(X_0)):
            X_0[n] /= normalisation_factors[n]
        
        # Solve the minimisation problem with SciPy
        result = minimize(
            lambda X: self.calculate_cost(X, fitting_params, normalisation_factors, fixed_hydration), 
            X_0, 
            method = 'BFGS',
            options = {"xrtol": 1e-3})

        if not(result.success):
            print('WARNING: SciPy minimise did not converge!')

        # extract fitted values
        normalised_fitted_vals = result.x

        # un-normalised the fitted values
        fitted_vals = normalised_fitted_vals.copy()
        for n in range(len(X_0)):
            fitted_vals[n] = normalised_fitted_vals[n] * normalisation_factors[n]        

        # print some info to the screen
        print('Optimal parameters:')
        for val, param in zip(fitted_vals, fitting_params):
            print(f'{param} = {val:.4e}')


        return fitted_vals


    def calculate_cost(self, X, fitting_params, normalisation_factors, fixed_hydration):
        """
        Computes the objective function.  The compression of the
        material is assumed to be fast so that there is no loss
        of fluid.

        Inputs:

        X = array of values of the current fitting parameters
        
        fitting_params = a dictionary where the keys are strings
        that describe the parameters to fit and the values are
        initial guess.  
        
        normalisation_factors = an optional list of numerical values that
        can be used to normalise the parameters to improve the performance
        of the optimiser

        fixed_hydration = a flag that determines whether the initial
        hydration of the material should be kept constant during the
        fit


        Outputs:

        cost = a float with the value of the cost/objective function

        """

        # initiate the cost
        cost = 0

        # Update the model with the new parameter values
        for key in self.data:
            pars = self.data[key]["pars"]
            model = self.data[key]["model"]
            for value, param, factor in zip(X, fitting_params, normalisation_factors):
                pars.update(param, value * factor)
            model.assign(pars)
    
            # update hydration if required
            if fixed_hydration:
                chi_calc = ChiCalculator(model, pars)
                chi, beta_r, beta_z, phi_0 = chi_calc.solve(J_0 = 1 / (1 - pars.physical["phi_0"]))
                pars.update("chi", chi)
                pars.update("beta_r", beta_r)
                pars.update("beta_z", beta_z)
                pars.update("phi_0", phi_0)
                model.assign(pars)

            # load the data points to evaluate the stretch at
            lam_z = self.data[key]["stretch_data"]
            
            # compute radial stretch
            lam_r = 1 / np.sqrt(lam_z)

            # compute stresses and pressure
            S_r, _, S_z = model.mechanics.eval_stress(lam_r, lam_r, lam_z)
            p = lam_r * S_r

            # Calculate the total PK1 stress
            S_z_T = S_z - lam_r**2 * p

            # Compute the cost as the RMSE
            if pars.nondim:
                scaling = pars.scaling["stress"]
            else:
                scaling = 1
            cost += np.sqrt(np.mean((scaling * S_z_T - self.data[key]["stress_data"])**2))

        return cost