import math
from numbers import Number
from lt_utils.common import *
from torch.optim import Optimizer
from typing_extensions import override
from torch.optim.lr_scheduler import LRScheduler


class CustomLRSchedulerBase(LRScheduler):
    def __init__(
        self,
        optimizer: Optimizer,
        last_epoch: int = -1,
        floor_lr: float = 1e-7,
        ceil_lr: float = 1.0,
        initial_lr: Optional[float] = None,
        reset_cycle_gamma: float = 1.0,
    ):
        self.floor_lr = floor_lr
        self.ceil_lr = ceil_lr
        if initial_lr is not None:
            for p_group in self.optimizer.param_groups:
                p_group["initial_lr"] = initial_lr
            self.base_lrs = [x["initial_lr"] for x in self.optimizer.param_groups]
        self.reset_cycle_gamma = reset_cycle_gamma
        self.disabled = False
        self._last_lr = [x['lr'] for x in optimizer.param_groups]
        self.base_lrs = [x['lr'] for x in optimizer.param_groups]
        super().__init__(optimizer, last_epoch)

    def _clamp_lr(self, new_value: float):
        return min(max(new_value, self.floor_lr), self.ceil_lr)

    def _set_floor(self, new_value: float):
        self.floor_lr = float(new_value)
        self.disabled = False

    def reset_lr(self):
        self.disabled = False
        self.base_lrs = []
        self._last_lr = []
        for p_group in self.optimizer.param_groups:
            lr = p_group["initial_lr"] * self.reset_cycle_gamma
            p_group["initial_lr"] = lr
            p_group["lr"] = lr
            self.base_lrs.append(lr)
            self._last_lr.append(lr)

class WarmupDecayLR(CustomLRSchedulerBase):
    def __init__(
        self,
        optimizer: Optimizer,
        last_epoch: int = -1,
        warmup_steps: int = 128,
        floor_lr: float = 1e-7,
    ):
        self.warmup_steps = warmup_steps + (warmup_steps % 2)
        super().__init__(optimizer, last_epoch, floor_lr=floor_lr)

    @override
    def get_lr(self):
        if self.disabled or self._is_initial:
            return self.get_last_lr()
        elif self.last_epoch >= self.warmup_steps:
            self.disabled = True
            return self.get_last_lr()
        lrs = []
        step = self.last_epoch + 1
        # base = step / self.warmup_steps
        base = 1 + (-math.cos(math.pi * (step / self.warmup_steps)))
        for base_lr in self.base_lrs:
            lr = base_lr * 1.0 * base
            lrs.append(self._clamp_lr(lr))

        return lrs


class WarmupDecayWithResetsLR(CustomLRSchedulerBase):
    def __init__(
        self,
        optimizer: Optimizer,
        last_epoch: int = -1,
        warmup_steps: int = 128,
        total_resets: int = 3,
        floor_lr: float = 1e-7,
        fallback_decay_speed: Union[int, float] = 2,
        force_break_check: bool = False,
    ):
        self.warmup_steps = warmup_steps + (warmup_steps % 2)
        self.total_resets = int(max(total_resets, 1))
        self.current_resets = 0
        self.on_reverse = False
        self.warmed_steps = 0
        self.force_break_check = force_break_check
        self.fallback_decay_speed = fallback_decay_speed
        self.total_warmup_steps = int(self.warmup_steps * self.total_resets) + 1
        super().__init__(optimizer, last_epoch, floor_lr=floor_lr)

    def reset_lr(self):
        super().reset_lr()

    def _next_step(self):
        if self.on_reverse:
            self.warmed_steps -= self.fallback_decay_speed
        else:
            self.warmed_steps += 1

        if self.warmed_steps == 0:
            if self.last_epoch >= self.total_warmup_steps:
                self.disabled = True
                self.warmed_steps = self.warmup_steps

            self.on_reverse = False
        elif self.warmed_steps >= self.warmup_steps:
            if self.last_epoch >= self.total_warmup_steps:
                self.disabled = True
                self.warmed_steps = self.warmup_steps
            else:
                self.on_reverse = True
        elif self.force_break_check:
            if self.last_epoch >= self.total_warmup_steps:
                self.disabled = True
                self.warmed_steps = self.warmup_steps

    @override
    def get_lr(self):
        if self.disabled or self._is_initial:
            return self.get_last_lr()

        lrs = []

        self._next_step()
        base = 1 + (-math.cos(math.pi * (self.warmed_steps / self.warmup_steps)))
        for base_lr in self.base_lrs:
            lr = base_lr * base
            lrs.append(self._clamp_lr(lr))

        return lrs


class AdaptiveDropLR(LRScheduler):
    def __init__(
        self,
        optimizer,
        drop_factor=0.5,
        patience=10,
        min_lr=1e-6,
        cooldown=5,
        last_epoch=-1,
    ):
        self.drop_factor = drop_factor
        self.patience = patience
        self.min_lr = min_lr
        self.cooldown = cooldown
        self.cooldown_counter = 0
        self.best_loss = float("inf")
        self.bad_steps = 0
        super().__init__(optimizer, last_epoch)

    def step(self, val_loss=None):
        if val_loss is not None:
            if val_loss < self.best_loss:
                self.best_loss = val_loss
                self.bad_steps = 0
                self.cooldown_counter = 0
            else:
                self.bad_steps += 1
                if self.bad_steps >= self.patience and self.cooldown_counter == 0:
                    for i, group in enumerate(self.optimizer.param_groups):
                        new_lr = max(group["lr"] * self.drop_factor, self.min_lr)
                        group["lr"] = new_lr
                    self.cooldown_counter = self.cooldown
                    self.bad_steps = 0
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1

    def get_lr(self):
        return [group["lr"] for group in self.optimizer.param_groups]


class WaveDecayLR(CustomLRSchedulerBase):
    def __init__(
        self,
        optimizer: Optimizer,
        target_lr: float = 1e-5,
        floor_lr: float = 1e-7,
        ceil_lr: float = 0.1,
        decay_rate: float = 0.1,
        wave_amplitude: float = 0.1,
        period: int = 90,
        last_epoch: int = -1,
        damp: float = 0.1,
    ):
        assert decay_rate != 0.0, "decay_rate must be non-zero"

        self.target_lr = target_lr
        self.decay_rate = decay_rate
        self.wave_amplitude = wave_amplitude
        self.period = period
        self.disabled = False
        self.damp = damp
        super().__init__(optimizer, last_epoch, floor_lr=floor_lr, ceil_lr=ceil_lr)

    @override
    def get_lr(self):
        if self.disabled or self._is_initial:
            return self.get_last_lr()
        step = self.last_epoch + 1
        cycles = step / self.period
        t = step % self.period

        exp_cycle_decay = math.exp(-self.decay_rate * cycles)
        phase = 2 * math.pi * (self.damp + t / self.period)
        wave = math.sin(phase) * math.cos(phase)

        lrs = []
        centers = []
        for base in self.base_lrs:
            center = base * exp_cycle_decay
            centers.append(center)
            amp = self.wave_amplitude * center
            lr = self._clamp_lr(center + amp * wave)
            lrs.append(lr)
        if min(centers) * 0.995 <= self.target_lr:
            self.disabled = True
            return [max(x, self.target_lr) for x in lrs]
        return lrs


class FloorExponentialLR(CustomLRSchedulerBase):
    """Modified version from exponential lr, to have a minimum and reset functions.

    Decays the learning rate of each parameter group by gamma every epoch.

    When last_epoch=-1, sets initial lr as lr.

    Args:
        optimizer (Optimizer): Wrapped optimizer.
        gamma (float): Multiplicative factor of learning rate decay.
        last_epoch (int): The index of last epoch. Default: -1.
        floor_lr (float): the value that will determine the minimum lr that this scheduler can reach.
    """

    def __init__(
        self,
        optimizer: Optimizer,
        gamma: float = 0.99998,
        last_epoch: int = -1,
        floor_lr: float = 1e-7,
    ):
        self.gamma = gamma

        super().__init__(optimizer, last_epoch, floor_lr=floor_lr)

    @override
    def get_lr(self):
        if self.disabled or self._is_initial:
            return self.get_last_lr()
        lrs = []
        for current_lr in self.get_last_lr():
            new_lr = current_lr * self.gamma
            lrs.append(self._clamp_lr(new_lr))

        if min(lrs) * 0.99 <= self.floor_lr:
            self.disabled = True
        return lrs


class FloorExponentialWithResetsLR(CustomLRSchedulerBase):
    """Modified version from exponential lr, to have a minimum and reset functions.

    Decays the learning rate of each parameter group by gamma every epoch.

    When last_epoch=-1, sets initial lr as lr.

    Args:
        optimizer (Optimizer): Wrapped optimizer.
        gamma (float): Multiplicative factor of learning rate decay.
        last_epoch (int): The index of last epoch. Default: -1.
        floor_lr (float): the value that will determine the minimum lr that this scheduler can reach.
    """

    def __init__(
        self,
        optimizer: Optimizer,
        gamma: float = 0.99,
        last_epoch: int = -1,
        floor_lr: float = 1e-7,
        max_resets: int = -1,
        gamma_reset: float = 0.95
    ):
        self.gamma = gamma
        self.floor_lr = floor_lr
        self.max_resets = max_resets
        self.total_resets = 0
        super().__init__(optimizer, last_epoch, floor_lr=floor_lr, reset_cycle_gamma=gamma_reset)

    def _has_hit_floor(self):
        return all(
            list(map(lambda x: x["lr"] <= self.floor_lr, self.optimizer.param_groups))
        )

    def reset_lr(self):
        super().reset_lr()
        if self.max_resets > 0 and self.max_resets <= self.total_resets:
            self.disabled = True
            

    def set_floor(self, new_value: float):
        assert isinstance(new_value, Number)
        self.floor_lr = new_value

    @override
    def get_lr(self):
        if self.disabled or self._is_initial:
            return self.get_last_lr()

        if min(self.get_last_lr()) * 0.99 <= self.floor_lr:
            self.total_resets += 1
            self.reset_lr()
        lrs = []
        for current_lr in self.get_last_lr():
            new_lr = current_lr * self.gamma
            lrs.append(self._clamp_lr(new_lr))


        return lrs


class FloorStepLR(CustomLRSchedulerBase):
    """Decays the learning rate of each parameter group by gamma every step_size epochs.

    Notice that such decay can happen simultaneously with other changes to the learning rate
    from outside this scheduler. When last_epoch=-1, sets initial lr as lr.

    Args:
        optimizer (Optimizer): Wrapped optimizer.
        step_size (int): Period of learning rate decay.
        gamma (float): Multiplicative factor of learning rate decay.
            Default: 0.1.
        last_epoch (int): The index of last epoch. Default: -1.

    Example:
        >>> # xdoctest: +SKIP
        >>> # Assuming optimizer uses lr = 0.05 for all groups
        >>> # lr = 0.05     if epoch < 30
        >>> # lr = 0.005    if 30 <= epoch < 60
        >>> # lr = 0.0005   if 60 <= epoch < 90
        >>> # ...
        >>> scheduler = StepLR(optimizer, step_size=30, gamma=0.1)
        >>> for epoch in range(100):
        >>>     train(...)
        >>>     validate(...)
        >>>     scheduler.step()

    .. image:: ../scripts/lr_scheduler_images/StepLR.png
    """

    def __init__(
        self,
        optimizer: Optimizer,
        step_size: int,
        gamma: float = 0.95,
        last_epoch: int = -1,
        floor_lr: float = 1e-7,
        ceil_lr: float = 1,
        initial_lr: float | None = None,
    ) -> None:  # noqa: D107
        self.step_size = step_size
        self.gamma = gamma
        super().__init__(
            optimizer,
            last_epoch,
            floor_lr=floor_lr,
            ceil_lr=ceil_lr,
            initial_lr=initial_lr,
        )

    @override
    def get_lr(self) -> list[float]:
        if self.disabled or self._is_initial:

            return self.get_last_lr()
        lrs = []
        for last_lr in self.get_last_lr():
            new_lr = last_lr * self.gamma ** (self.last_epoch // self.step_size)
            lrs.append(self._clamp_lr(new_lr))

        if min(lrs)  * 0.99<= self.floor_lr:
            self.disabled = True
        return lrs
