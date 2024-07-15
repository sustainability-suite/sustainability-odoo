# © 2021 Open Net Sarl
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from . import models
from . import tests


def post_init_hook(env):
    """Create `carbon.line.origin` records if demo data"""
    if env.ref("base.user_demo", raise_if_not_found=False):
        moves = env["account.move"].search([])
        for move in moves:
            move.action_recompute_carbon()
