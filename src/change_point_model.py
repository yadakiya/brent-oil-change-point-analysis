"""
Bayesian change point detection model using PyMC.
"""

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, Dict, List, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChangePointModel:
    """
    Bayesian change point detection for time series data.
    """
    
    def __init__(self, data: np.ndarray, dates: pd.DatetimeIndex = None,
                 model_type: str = 'single'):
        """
        Initialize ChangePointModel.
        
        Args:
            data: Array of log returns
            dates: DatetimeIndex for the data
            model_type: 'single' or 'multiple'
        """
        self.data = data
        self.dates = dates
        self.model_type = model_type
        self.n = len(data)
        self.trace = None
        self.model = None
        
    def build_single_change_point_model(self) -> pm.Model:
        """
        Build single change point model with PyMC.
        
        Returns:
            PyMC Model
        """
        n = self.n
        idx = np.arange(n)
        
        with pm.Model() as model:
            # Prior for switch point (uniform over all days)
            tau = pm.DiscreteUniform('tau', lower=0, upper=n)
            
            # Priors for means before and after change
            mu_1 = pm.Normal('mu_1', mu=0, sigma=0.5)
            mu_2 = pm.Normal('mu_2', mu=0, sigma=0.5)
            
            # Prior for sigma (volatility)
            sigma = pm.HalfNormal('sigma', sigma=0.5)
            
            # Deterministic switch
            mu = pm.math.switch(tau >= idx, mu_1, mu_2)
            
            # Likelihood
            returns = pm.Normal('returns', mu=mu, sigma=sigma, observed=self.data)
            
        self.model = model
        return model
    
    def build_multiple_change_point_model(self, n_changepoints: int = 3) -> pm.Model:
        """
        Build multiple change point model with PyMC.
        
        Args:
            n_changepoints: Number of change points to detect
            
        Returns:
            PyMC Model
        """
        n = self.n
        idx = np.arange(n)
        
        with pm.Model() as model:
            # Priors for change points
            tau = pm.DiscreteUniform('tau', lower=0, upper=n, shape=n_changepoints)
            tau_sorted = pm.Deterministic('tau_sorted', pm.math.sort(tau))
            
            # Priors for means of each segment
            mu = pm.Normal('mu', mu=0, sigma=0.5, shape=n_changepoints + 1)
            
            # Prior for sigma
            sigma = pm.HalfNormal('sigma', sigma=0.5)
            
            # Assign each point to a segment
            # This is a simplified version - for more robust multiple CP detection,
            # you'd want to use a more sophisticated approach
            mu_segment = mu[0]  # Placeholder
            
            # Likelihood
            returns = pm.Normal('returns', mu=mu_segment, sigma=sigma, observed=self.data)
            
        self.model = model
        return model
    
    def fit(self, n_samples: int = 2000, n_tune: int = 1000,
            n_chains: int = 4, random_seed: int = 42) -> az.InferenceData:
        """
        Fit the change point model using MCMC.
        
        Args:
            n_samples: Number of posterior samples
            n_tune: Number of tuning samples
            n_chains: Number of MCMC chains
            random_seed: Random seed for reproducibility
            
        Returns:
            InferenceData object
        """
        if self.model is None:
            if self.model_type == 'single':
                self.build_single_change_point_model()
            else:
                self.build_multiple_change_point_model()
        
        logger.info(f"Fitting {self.model_type} change point model...")
        
        with self.model:
            self.trace = pm.sample(
                draws=n_samples,
                tune=n_tune,
                chains=n_chains,
                random_seed=random_seed,
                return_inferencedata=True
            )
        
        logger.info("Model fitting complete")
        return self.trace
    
    def check_convergence(self) -> Dict:
        """
        Check MCMC convergence using R-hat values.
        
        Returns:
            Dictionary with convergence metrics
        """
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        summary = az.summary(self.trace)
        
        # Check R-hat values
        r_hat = summary['r_hat']
        max_r_hat = r_hat.max()
        n_bad = (r_hat > 1.01).sum()
        
        convergence_results = {
            'max_r_hat': max_r_hat,
            'n_parameters': len(r_hat),
            'n_bad_r_hat': n_bad,
            'converged': max_r_hat < 1.01,
            'summary': summary
        }
        
        logger.info(f"Convergence check: max R-hat = {max_r_hat:.4f}")
        logger.info(f"Converged: {convergence_results['converged']}")
        
        return convergence_results
    
    def get_change_points(self, threshold: float = 0.5) -> List[int]:
        """
        Extract change point indices from posterior.
        
        Args:
            threshold: Probability threshold for change point detection
            
        Returns:
            List of change point indices
        """
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        if self.model_type == 'single':
            # Get posterior for tau
            tau_posterior = self.trace.posterior['tau'].values.flatten()
            
            # Find most probable change point
            tau_mode = int(pd.Series(tau_posterior).mode()[0])
            
            # Calculate posterior probability
            posterior_prob = (tau_posterior == tau_mode).mean()
            
            if posterior_prob >= threshold:
                return [tau_mode]
            else:
                return []
        
        else:
            # For multiple change points
            tau_posterior = self.trace.posterior['tau_sorted'].values
            
            # Get modes for each change point
            change_points = []
            for i in range(tau_posterior.shape[1]):
                tau_i = tau_posterior[:, i].flatten()
                tau_mode = int(pd.Series(tau_i).mode()[0])
                posterior_prob = (tau_i == tau_mode).mean()
                
                if posterior_prob >= threshold:
                    change_points.append(tau_mode)
            
            return sorted(change_points)
    
    def get_parameter_estimates(self) -> Dict:
        """
        Get posterior estimates for model parameters.
        
        Returns:
            Dictionary with parameter estimates and credible intervals
        """
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        summary = az.summary(self.trace, hdi_prob=0.95)
        
        estimates = {}
        for param in summary.index:
            estimates[param] = {
                'mean': summary.loc[param, 'mean'],
                'sd': summary.loc[param, 'sd'],
                'hdi_lower': summary.loc[param, 'hdi_3%'],
                'hdi_upper': summary.loc[param, 'hdi_97%'],
                'r_hat': summary.loc[param, 'r_hat']
            }
        
        return estimates
    
    def plot_results(self, save_path: str = None) -> None:
        """
        Plot model results including trace, posterior, and change point.
        
        Args:
            save_path: Optional path to save the figure
        """
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # Trace plot for tau
        az.plot_trace(self.trace, var_names=['tau'], axes=axes[0, :])
        axes[0, 0].set_title('Trace Plot - tau')
        
        # Posterior distribution of tau
        az.plot_posterior(self.trace, var_names=['tau'], ax=axes[1, 0])
        axes[1, 0].set_title('Posterior Distribution - tau')
        
        # Posterior of mu_1 and mu_2
        if self.model_type == 'single':
            az.plot_posterior(self.trace, var_names=['mu_1', 'mu_2'], 
                            ax=axes[1, 1])
            axes[1, 1].set_title('Posterior Distributions - μ₁, μ₂')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Figure saved to {save_path}")
        
        plt.show()
    
    def generate_impact_statement(self, df: pd.DataFrame) -> str:
        """
        Generate a natural language impact statement.
        
        Args:
            df: Original DataFrame with price data
            
        Returns:
            Impact statement string
        """
        if self.trace is None:
            raise ValueError("Model not fitted. Call fit() first.")
        
        # Get change points
        cp_indices = self.get_change_points()
        
        if not cp_indices:
            return "No significant change points detected."
        
        # Get parameter estimates
        estimates = self.get_parameter_estimates()
        
        if self.model_type == 'single' and len(cp_indices) == 1:
            cp_idx = cp_indices[0]
            cp_date = self.dates[cp_idx]
            
            mu_1 = estimates['mu_1']['mean']
            mu_2 = estimates['mu_2']['mean']
            
            # Get price levels
            before_price = df['Price'].iloc[cp_idx - 30:cp_idx].mean()
            after_price = df['Price'].iloc[cp_idx:cp_idx + 30].mean()
            
            price_change = after_price - before_price
            percent_change = (price_change / before_price) * 100
            
            statement = f"""
            ## Change Point Impact Statement
            
            The Bayesian change point model detected a structural break at approximately {cp_date.strftime('%Y-%m-%d')}.
            
            **Parameter Estimates:**
            - Before change (μ₁): {mu_1:.6f} (95% HDI: [{estimates['mu_1']['hdi_lower']:.6f}, {estimates['mu_1']['hdi_upper']:.6f}])
            - After change (μ₂): {mu_2:.6f} (95% HDI: [{estimates['mu_2']['hdi_lower']:.6f}, {estimates['mu_2']['hdi_upper']:.6f}])
            
            **Price Impact:**
            - Average price before: ${before_price:.2f}
            - Average price after: ${after_price:.2f}
            - Change: ${price_change:.2f} ({percent_change:.1f}%)
            
            **Interpretation:**
            The model indicates a {abs(percent_change):.1f}% {'increase' if price_change > 0 else 'decrease'} in Brent oil prices around this period.
            """
            
            return statement
        
        else:
            # Multiple change points
            statements = ["## Multiple Change Points Detected\n"]
            for i, cp_idx in enumerate(cp_indices):
                cp_date = self.dates[cp_idx]
                statements.append(f"\n**Change Point {i+1}**: {cp_date.strftime('%Y-%m-%d')}")
            
            return "\n".join(statements)
    
    def save_results(self, output_dir: str = "results/") -> None:
        """
        Save model results to disk.
        
        Args:
            output_dir: Directory to save results
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save trace
        if self.trace is not None:
            az.to_netcdf(self.trace, output_dir / "trace.nc")
        
        # Save parameter estimates
        if hasattr(self, 'trace') and self.trace is not None:
            estimates = self.get_parameter_estimates()
            estimates_df = pd.DataFrame(estimates).T
            estimates_df.to_csv(output_dir / "parameter_estimates.csv")
        
        logger.info(f"Results saved to {output_dir}")

# Example usage
if __name__ == "__main__":
    from data_loader import DataLoader
    
    # Load data
    loader = DataLoader()
    df = loader.load_data()
    returns = loader.get_log_returns()
    dates = loader.get_dates()
    
    # Create and fit model
    cp_model = ChangePointModel(returns, dates, model_type='single')
    cp_model.fit(n_samples=2000, n_tune=1000)
    
    # Check convergence
    convergence = cp_model.check_convergence()
    print(f"Converged: {convergence['converged']}")
    
    # Get change points
    cp_indices = cp_model.get_change_points()
    if cp_indices:
        cp_date = dates[cp_indices[0]]
        print(f"Change point detected: {cp_date}")
    
    # Generate impact statement
    statement = cp_model.generate_impact_statement(df)
    print(statement)
    
    # Plot results
    cp_model.plot_results()