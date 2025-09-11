"""
Physics loss functions for common physical systems.

This module provides pre-defined physics loss functions for various
physical systems including fluid dynamics, heat transfer, and wave equations.
"""

from __future__ import annotations

import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple, Union, Callable
import numpy as np


class PhysicsLoss:
    """
    Collection of physics loss functions for common physical systems.
    """
    
    @staticmethod
    def heat_equation_1d(
        x: torch.Tensor,
        model: nn.Module,
        thermal_diffusivity: float = 1.0
    ) -> torch.Tensor:
        """
        1D Heat equation: ∂u/∂t = α ∂²u/∂x²
        
        Args:
            x: Input tensor [batch_size, 2] where x[:, 0] = x, x[:, 1] = t
            model: Neural network model
            thermal_diffusivity: Thermal diffusivity coefficient α
            
        Returns:
            Physics loss
        """
        x.requires_grad_(True)
        u = model(x)
        
        # Compute derivatives
        u_t = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), 
                                 create_graph=True, retain_graph=True)[0][:, 1]
        u_x = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), 
                                 create_graph=True, retain_graph=True)[0][:, 0]
        
        # Second derivative with respect to x
        u_xx = torch.autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x), 
                                  create_graph=True, retain_graph=True)[0][:, 0]
        
        # Heat equation residual
        residual = u_t - thermal_diffusivity * u_xx
        return torch.mean(residual**2)
    
    @staticmethod
    def wave_equation_1d(
        x: torch.Tensor,
        model: nn.Module,
        wave_speed: float = 1.0
    ) -> torch.Tensor:
        """
        1D Wave equation: ∂²u/∂t² = c² ∂²u/∂x²
        
        Args:
            x: Input tensor [batch_size, 2] where x[:, 0] = x, x[:, 1] = t
            model: Neural network model
            wave_speed: Wave speed c
            
        Returns:
            Physics loss
        """
        x.requires_grad_(True)
        u = model(x)
        
        # First derivatives
        u_t = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), 
                                 create_graph=True, retain_graph=True)[0][:, 1]
        u_x = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), 
                                 create_graph=True, retain_graph=True)[0][:, 0]
        
        # Second derivatives
        u_tt = torch.autograd.grad(u_t, x, grad_outputs=torch.ones_like(u_t), 
                                  create_graph=True, retain_graph=True)[0][:, 1]
        u_xx = torch.autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x), 
                                  create_graph=True, retain_graph=True)[0][:, 0]
        
        # Wave equation residual
        residual = u_tt - (wave_speed**2) * u_xx
        return torch.mean(residual**2)
    
    @staticmethod
    def burgers_equation_1d(
        x: torch.Tensor,
        model: nn.Module,
        viscosity: float = 0.01
    ) -> torch.Tensor:
        """
        1D Burgers equation: ∂u/∂t + u ∂u/∂x = ν ∂²u/∂x²
        
        Args:
            x: Input tensor [batch_size, 2] where x[:, 0] = x, x[:, 1] = t
            model: Neural network model
            viscosity: Viscosity coefficient ν
            
        Returns:
            Physics loss
        """
        x.requires_grad_(True)
        u = model(x)
        
        # First derivatives
        u_t = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), 
                                 create_graph=True, retain_graph=True)[0][:, 1]
        u_x = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), 
                                 create_graph=True, retain_graph=True)[0][:, 0]
        
        # Second derivative with respect to x
        u_xx = torch.autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x), 
                                  create_graph=True, retain_graph=True)[0][:, 0]
        
        # Burgers equation residual
        residual = u_t + u * u_x - viscosity * u_xx
        return torch.mean(residual**2)
    
    @staticmethod
    def navier_stokes_2d(
        x: torch.Tensor,
        model: nn.Module,
        viscosity: float = 0.01,
        density: float = 1.0
    ) -> torch.Tensor:
        """
        2D Navier-Stokes equations for incompressible flow.
        
        Args:
            x: Input tensor [batch_size, 3] where x[:, 0] = x, x[:, 1] = y, x[:, 2] = t
            model: Neural network model (outputs [u, v, p])
            viscosity: Kinematic viscosity
            density: Fluid density
            
        Returns:
            Physics loss
        """
        x.requires_grad_(True)
        output = model(x)
        u = output[:, 0:1]  # x-velocity
        v = output[:, 1:2]  # y-velocity
        p = output[:, 2:3]  # pressure
        
        # First derivatives
        u_x = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), 
                                 create_graph=True, retain_graph=True)[0][:, 0:1]
        u_y = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), 
                                 create_graph=True, retain_graph=True)[0][:, 1:2]
        u_t = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), 
                                 create_graph=True, retain_graph=True)[0][:, 2:3]
        
        v_x = torch.autograd.grad(v, x, grad_outputs=torch.ones_like(v), 
                                 create_graph=True, retain_graph=True)[0][:, 0:1]
        v_y = torch.autograd.grad(v, x, grad_outputs=torch.ones_like(v), 
                                 create_graph=True, retain_graph=True)[0][:, 1:2]
        v_t = torch.autograd.grad(v, x, grad_outputs=torch.ones_like(v), 
                                 create_graph=True, retain_graph=True)[0][:, 2:3]
        
        p_x = torch.autograd.grad(p, x, grad_outputs=torch.ones_like(p), 
                                 create_graph=True, retain_graph=True)[0][:, 0:1]
        p_y = torch.autograd.grad(p, x, grad_outputs=torch.ones_like(v), 
                                 create_graph=True, retain_graph=True)[0][:, 1:2]
        
        # Second derivatives
        u_xx = torch.autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x), 
                                  create_graph=True, retain_graph=True)[0][:, 0:1]
        u_yy = torch.autograd.grad(u_y, x, grad_outputs=torch.ones_like(u_y), 
                                  create_graph=True, retain_graph=True)[0][:, 1:2]
        
        v_xx = torch.autograd.grad(v_x, x, grad_outputs=torch.ones_like(v_x), 
                                  create_graph=True, retain_graph=True)[0][:, 0:1]
        v_yy = torch.autograd.grad(v_y, x, grad_outputs=torch.ones_like(v_y), 
                                  create_graph=True, retain_graph=True)[0][:, 1:2]
        
        # Continuity equation: ∇·u = 0
        continuity = u_x + v_y
        
        # x-momentum equation
        x_momentum = u_t + u * u_x + v * u_y + (1/density) * p_x - viscosity * (u_xx + u_yy)
        
        # y-momentum equation
        y_momentum = v_t + u * v_x + v * v_y + (1/density) * p_y - viscosity * (v_xx + v_yy)
        
        # Total residual
        residual = torch.mean(continuity**2) + torch.mean(x_momentum**2) + torch.mean(y_momentum**2)
        return residual
    
    @staticmethod
    def schrodinger_equation_1d(
        x: torch.Tensor,
        model: nn.Module,
        hbar: float = 1.0,
        mass: float = 1.0
    ) -> torch.Tensor:
        """
        1D Schrödinger equation: iℏ ∂ψ/∂t = -ℏ²/(2m) ∂²ψ/∂x² + V(x)ψ
        
        Args:
            x: Input tensor [batch_size, 2] where x[:, 0] = x, x[:, 1] = t
            model: Neural network model (outputs complex wave function)
            hbar: Reduced Planck constant
            mass: Particle mass
            potential: Potential energy function V(x)
            
        Returns:
            Physics loss
        """
        x.requires_grad_(True)
        output = model(x)
        psi_real = output[:, 0:1]
        psi_imag = output[:, 1:2]
        psi = torch.complex(psi_real, psi_imag)
        
        # First derivatives
        psi_t = torch.autograd.grad(psi_real, x, grad_outputs=torch.ones_like(psi_real), 
                                   create_graph=True, retain_graph=True)[0][:, 1:2] + \
                1j * torch.autograd.grad(psi_imag, x, grad_outputs=torch.ones_like(psi_imag), 
                                        create_graph=True, retain_graph=True)[0][:, 1:2]
        
        psi_x = torch.autograd.grad(psi_real, x, grad_outputs=torch.ones_like(psi_real), 
                                   create_graph=True, retain_graph=True)[0][:, 0:1] + \
                1j * torch.autograd.grad(psi_imag, x, grad_outputs=torch.ones_like(psi_imag), 
                                        create_graph=True, retain_graph=True)[0][:, 0:1]
        
        # Second derivative with respect to x
        psi_xx = torch.autograd.grad(psi_x.real, x, grad_outputs=torch.ones_like(psi_x.real), 
                                    create_graph=True, retain_graph=True)[0][:, 0:1] + \
                 1j * torch.autograd.grad(psi_x.imag, x, grad_outputs=torch.ones_like(psi_x.imag), 
                                         create_graph=True, retain_graph=True)[0][:, 0:1]
        
        # Simple harmonic oscillator potential V(x) = 0.5 * x²
        V = 0.5 * x[:, 0:1]**2
        
        # Schrödinger equation residual
        residual = 1j * hbar * psi_t + (hbar**2) / (2 * mass) * psi_xx - V * psi
        return torch.mean(torch.abs(residual)**2)
    
    @staticmethod
    def conservation_law_1d(
        x: torch.Tensor,
        model: nn.Module,
        flux_function: Callable = None
    ) -> torch.Tensor:
        """
        1D Conservation law: ∂u/∂t + ∂f(u)/∂x = 0
        
        Args:
            x: Input tensor [batch_size, 2] where x[:, 0] = x, x[:, 1] = t
            model: Neural network model
            flux_function: Flux function f(u)
            
        Returns:
            Physics loss
        """
        if flux_function is None:
            # Default: linear advection f(u) = u
            flux_function = lambda u: u
        
        x.requires_grad_(True)
        u = model(x)
        
        # First derivatives
        u_t = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), 
                                 create_graph=True, retain_graph=True)[0][:, 1]
        u_x = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), 
                                 create_graph=True, retain_graph=True)[0][:, 0]
        
        # Flux and its derivative
        f = flux_function(u)
        f_x = torch.autograd.grad(f, x, grad_outputs=torch.ones_like(f), 
                                 create_graph=True, retain_graph=True)[0][:, 0]
        
        # Conservation law residual
        residual = u_t + f_x
        return torch.mean(residual**2)
    
    @staticmethod
    def elasticity_2d(
        x: torch.Tensor,
        model: nn.Module,
        young_modulus: float = 1.0,
        poisson_ratio: float = 0.3
    ) -> torch.Tensor:
        """
        2D Linear elasticity equations.
        
        Args:
            x: Input tensor [batch_size, 2] where x[:, 0] = x, x[:, 1] = y
            model: Neural network model (outputs [u, v] displacements)
            young_modulus: Young's modulus E
            poisson_ratio: Poisson's ratio ν
            
        Returns:
            Physics loss
        """
        x.requires_grad_(True)
        output = model(x)
        u = output[:, 0:1]  # x-displacement
        v = output[:, 1:2]  # y-displacement
        
        # First derivatives
        u_x = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), 
                                 create_graph=True, retain_graph=True)[0][:, 0:1]
        u_y = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), 
                                 create_graph=True, retain_graph=True)[0][:, 1:2]
        
        v_x = torch.autograd.grad(v, x, grad_outputs=torch.ones_like(v), 
                                 create_graph=True, retain_graph=True)[0][:, 0:1]
        v_y = torch.autograd.grad(v, x, grad_outputs=torch.ones_like(v), 
                                 create_graph=True, retain_graph=True)[0][:, 1:2]
        
        # Second derivatives
        u_xx = torch.autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x), 
                                  create_graph=True, retain_graph=True)[0][:, 0:1]
        u_yy = torch.autograd.grad(u_y, x, grad_outputs=torch.ones_like(u_y), 
                                  create_graph=True, retain_graph=True)[0][:, 1:2]
        u_xy = torch.autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x), 
                                  create_graph=True, retain_graph=True)[0][:, 1:2]
        
        v_xx = torch.autograd.grad(v_x, x, grad_outputs=torch.ones_like(v_x), 
                                  create_graph=True, retain_graph=True)[0][:, 0:1]
        v_yy = torch.autograd.grad(v_y, x, grad_outputs=torch.ones_like(v_y), 
                                  create_graph=True, retain_graph=True)[0][:, 1:2]
        v_xy = torch.autograd.grad(v_x, x, grad_outputs=torch.ones_like(v_x), 
                                  create_graph=True, retain_graph=True)[0][:, 1:2]
        
        # Lamé parameters
        mu = young_modulus / (2 * (1 + poisson_ratio))
        lam = young_modulus * poisson_ratio / ((1 + poisson_ratio) * (1 - 2 * poisson_ratio))
        
        # Equilibrium equations (assuming no body forces)
        x_equilibrium = (lam + mu) * (u_xx + v_xy) + mu * (u_xx + u_yy)
        y_equilibrium = (lam + mu) * (u_xy + v_yy) + mu * (v_xx + v_yy)
        
        # Total residual
        residual = torch.mean(x_equilibrium**2) + torch.mean(y_equilibrium**2)
        return residual
