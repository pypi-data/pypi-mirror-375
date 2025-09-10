from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, Union, Optional

import numpy as np
import torch
import wandb


class Target(ABC):
    """Abstract base for target value calculation in loss balancing."""

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def get_target(self, **target_input: Any) -> float:
        """Calculate target value.

        Args:
            target_input: Input parameters for target calculation

        Returns:
            Target value
        """
        pass


class RelativeTarget(Target):
    """Target proportional to reference value: target = ratio * reference_value."""

    def __init__(self, ratio: float = 1) -> None:
        """Initialize relative target.

        Args:
            ratio: Scaling factor (1.0 = equal, 2.0 = 2x reference)
        """
        self.ratio = ratio

    def get_target(self, **target_input: Any) -> float:
        """Return scaled reference value.

        Args:
            target_reference_values: Reference value to scale

        Returns:
            ratio * target_reference_values
        """
        target_reference_values = target_input.pop("target_reference_values", None)
        return self.ratio * target_reference_values


class ConstantTarget(Target):
    """Fixed target value."""

    def __init__(self, value: float) -> None:
        """Initialize constant target.

        Args:
            value: Fixed target value
        """
        self.target = value

    def get_target(self, **target_input: Any) -> float:
        """Return constant target value."""
        return self.target


class LinearTrajectoryTarget(Target):
    """Target that changes linearly from initial to final value over time."""

    def __init__(self, initial: float, final: float, num_steps: int) -> None:
        """Initialize linear trajectory.

        Args:
            initial: Starting value
            final: Final value after num_steps
            num_steps: Steps to reach final value
        """
        self.initial = initial
        self.target = initial
        self.num_steps = num_steps
        self.cur_step = 0
        self.step = (final - initial) / float(num_steps)

    def get_target(self, **target_input: Any) -> float:
        """Return current target and advance trajectory.

        Args:
            step: Optional explicit step number

        Returns:
            Current target value
        """
        step = target_input.pop("step", None)
        if step is not None:
            step = min(step, self.num_steps)
            return self.initial + (step * self.step)
        else:
            self.cur_step += 1
            if self.cur_step <= self.num_steps:
                self.target += self.step
            return self.target


class LossWeighter(ABC):
    """Abstract base for loss weighting strategies."""

    @abstractmethod
    def get_balance_param(self, **kwargs: Any) -> Tuple[float, Dict[str, float]]:
        """Get balance parameter for loss weighting.

        Returns:
            Tuple of (balance_parameter, info_dict)
        """
        pass

    def get_combined_loss(self, loss1: Union[float, torch.Tensor], loss2: Union[float, torch.Tensor], alpha: float) -> Union[float, torch.Tensor]:
        """Compute weighted combination of losses.

        Args:
            loss1: First loss (controlled by alpha)
            loss2: Second loss (controlled by 1-alpha)
            alpha: Balance parameter [0,1]

        Returns:
            Combined loss: alpha * loss1 + (1-alpha) * loss2
        """

        return alpha * loss1 + (1 - alpha) * loss2


class FixedLossWeighter(LossWeighter):
    """Fixed balance parameter weighter."""

    def __init__(self, initial_balance: float = 0.5) -> None:
        """Initialize fixed weighter.

        Args:
            initial_balance: Fixed balance parameter
        """
        self.initial_balance = initial_balance

    def get_balance_param(self, **kwargs: Any) -> Tuple[float, Dict[str, float]]:
        """Return fixed balance parameter.

        Returns:
            Tuple of (balance_parameter, empty_info_dict)
        """
        return self.initial_balance, {}


class PDLossWeighter(LossWeighter):
    """PD controller for automatic loss balancing.

    Uses proportional-derivative control to adjust alpha to keep
    controlled value close to target: alpha += kp*error + kd*derivative
    """

    def __init__(
        self,
        target: Target,
        kp: float = 0.001,
        kd: float = 0.02,
        initial_balance: float = 0.5,
        len_errors: int = 5,
        min_alpha: float = 0,
        max_alpha: float = 1,
        arithmetic_error: bool = True,
        error_max: Optional[float] = None,
        derivative_max: Optional[float] = None,
        update_max: Optional[float] = None,
    ) -> None:
        """Initialize PD controller.

        Args:
            target: Target computation strategy
            kp: Proportional gain (response to current error)
            kd: Derivative gain (response to error trend)
            initial_balance: Starting alpha (0=loss2 only, 1=loss1 only)
            len_errors: Error history length for derivative
            min_alpha: Minimum alpha value
            max_alpha: Maximum alpha value
            arithmetic_error: If True use error=actual-target, else geometric
            error_max: Error clipping bound
            derivative_max: Derivative clipping bound
            update_max: Maximum alpha update per step
        """
        assert min_alpha <= initial_balance <= max_alpha
        assert 0 <= min_alpha <= max_alpha <= 1
        assert error_max is None or error_max > 0
        assert derivative_max is None or derivative_max >= 0

        self.target = target
        self.alpha = initial_balance
        self.kp = kp
        self.kd = kd
        self.len_errors = len_errors
        self.min_alpha = min_alpha
        self.max_alpha = max_alpha
        self.arithmetic_error = arithmetic_error
        self.error_max = error_max
        self.derivative_max = derivative_max
        self.update_max = update_max
        self.errors: list[float] = []

    def get_error_and_deriv(
        self,
        measured_output: Union[float, torch.Tensor],
        **target_input_kwargs: Any,
    ) -> Tuple[float, float, float]:
        """Compute error and derivative for PD control.

        Args:
            measured_output: Current controlled value
            target_input_kwargs: Arguments for target calculation

        Returns:
            (error, derivative, target_value) tuple
        """
        target_value = self.target.get_target(**target_input_kwargs)
        if isinstance(measured_output, torch.Tensor):
            measured_output = measured_output.detach().cpu().item()

        if self.arithmetic_error:
            error = measured_output - target_value
        else:
            # Geometric error for scale-invariant control
            if target_value > measured_output:
                error = -target_value / (measured_output + 1e-2)
            else:
                error = measured_output / (target_value + 1e-2)

        if self.error_max:
            error = np.clip(error, -self.error_max, self.error_max)

        derivative = 0.0
        if len(self.errors) > self.len_errors:
            derivative = error - self.errors[0]
            if self.derivative_max:
                derivative = np.clip(
                    derivative,
                    -self.derivative_max,
                    self.derivative_max,
                )

            self.errors.pop(0)

        self.errors.append(error)

        return error, derivative, target_value

    def get_balance_param(
        self,
        measured_output: Union[float, torch.Tensor],
        **target_input_kwargs: Any,
    ) -> Tuple[float, Dict[str, float]]:
        """Update and return balance parameter using PD control.

        Args:
            measured_output: Current controlled value
            target_input_kwargs: Arguments for target calculation

        Returns:
            Tuple of (balance_parameter, info_dict) with controller diagnostics
        """
        error, derivative, target_value = self.get_error_and_deriv(
            measured_output, **target_input_kwargs
        )

        # PD control update
        update = (self.kp * error) + (self.kd * derivative)
        if self.update_max:
            update = np.clip(update, -self.update_max, self.update_max)

        self.alpha += update
        self.alpha = np.clip(self.alpha, self.min_alpha, self.max_alpha)

        info_dict = {
            "pd_controller/error": error,
            "pd_controller/kp": self.kp,
            "pd_controller/derivative": derivative,
            "pd_controller/kd": self.kd,
            "pd_controller/target": target_value,
        }
        return self.alpha, info_dict


class PLossWeighter(PDLossWeighter):
    """Proportional-only controller (PD with kd=0)."""

    def __init__(
        self,
        target: Target,
        kp: float = 0.001,
        initial_balance: float = 0.5,
        min_alpha: float = 0,
        max_alpha: float = 1,
        arithmetic_error: bool = False,
        error_max: Optional[float] = None,
        update_max: Optional[float] = None,
    ) -> None:
        """Initialize P-only controller.

        Args:
            target: Target computation strategy
            kp: Proportional gain
            initial_balance: Starting alpha value
            min_alpha: Minimum alpha
            max_alpha: Maximum alpha
            arithmetic_error: Error calculation method
            error_max: Error clipping bound
            update_max: Maximum alpha update per step
        """
        super().__init__(
            target=target,
            kp=kp,
            kd=0.0,
            initial_balance=initial_balance,
            len_errors=1,
            min_alpha=min_alpha,
            max_alpha=max_alpha,
            arithmetic_error=arithmetic_error,
            error_max=error_max,
            derivative_max=0.0,
            update_max=update_max,
        )
