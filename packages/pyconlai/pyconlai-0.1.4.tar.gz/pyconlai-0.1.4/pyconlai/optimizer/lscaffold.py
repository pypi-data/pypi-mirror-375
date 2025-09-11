import torch
from .mixin import ConLOptimizer


class LScaffold(ConLOptimizer):
    STATE_P = "state_p"

    def __init__(self, path, org_optimizer, parameters, inner_loop: int = 10):
        super(LScaffold, self).__init__(path, org_optimizer, parameters, inner_loop)

    def __setstate__(self, state):
        super(LScaffold, self).__setstate__(state)
        for group in self.param_groups:
            group.setdefault('nesterov', False)

    @torch.no_grad()
    def precondition(self):
        for group in self.param_groups:
            for i, p in enumerate(group['params']):
                if p.grad is None:
                    continue

                param_state = self.state[p]
                if 'c_i' not in param_state:
                    param_state['c_i'] = torch.zeros(p.size(), device=p.device).detach()
                if 'c_g' not in param_state:
                    param_state['c_g'] = torch.zeros(p.size(), device=p.device).detach()
                p.grad += param_state['c_i']

    @torch.no_grad()
    def aggregate(self, rcv_p):
        i = 0
        diff_sum = 0.

        snd_p = []
        state = None
        if rcv_p is not None:
            state = rcv_p[self.STATE_P]

        for group in self.param_groups:
            eta = group['eta']
            for p in group['params']:
                if p.grad is None:
                    continue

                if state is not None:
                    param_state = self.state[p]
                    if 'state_prv' not in param_state:
                        param_state['state_prv'] = torch.zeros(p.size(), device=p.device).detach()

                    coef = 1 / (self.inner_loop * self.lr)
                    c_p = param_state['c_i'] - param_state['c_g'] - coef * (param_state['state_prv'] - p.data)
                    param_state['c_g'] = (param_state['c_i'] + param_state['c_g']) / 2
                    param_state['c_i'] = c_p

                    r_p = state[i].to(p.device)
                    p.data = (r_p + p.data) / 2
                    param_state['state_prv'] = p.data.clone().detach()
                    diff_sum += self._criterion(r_p, p.data)

                    i += 1

                snd_p.append(p.data.clone().to("cpu"))

        self._diff_latest = diff_sum
        return {self.STATE_P: snd_p}
