from odoo import models

from ..services.keycloak import KeycloakService


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def create_keycloak_user(self):
        self.ensure_one()

        keycloak = KeycloakService(self.company_id)
        keycloak.create_keycloak_user(self.partner_id)

        self.create_user(self.partner_id)

    def create_user(self, partner):
        oauth_provider = self.env["auth.oauth.provider"].search(
            [("name", "=", "Keycloak")], limit=1
        )
        vals = {
            "partner_id": partner.id,
            "groups_id": [self.env.ref("base.group_portal").id],
            "login": partner.email,
            "lang": partner.lang,
            "oauth_provider_id": oauth_provider.id,
            "oauth_uid": partner.email,
        }
        self.env["res.users"].sudo().with_context(no_reset_password=True).create(vals)
