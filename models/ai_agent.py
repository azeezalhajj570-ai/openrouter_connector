from odoo import api, models


class AIAgent(models.Model):
    _inherit = 'ai.agent'

    @api.model
    def _get_llm_model_selection(self):
        selection = super()._get_llm_model_selection()
        openrouter_models = self.env['ai.openrouter.model'].search([('active', '=', True)])
        for model in openrouter_models:
            selection.append((model.external_id, f"[OpenRouter] {model.name}"))
        return selection

    def _register_hook(self):
        super()._register_hook()
        if 'llm_model' in self._fields:
            self._fields['llm_model'].selection = type(self)._get_llm_model_selection

    def _get_embedding_model(self):
        self.ensure_one()
        provider = self._get_provider()
        if provider == "openrouter":
            openrouter_provider = self.env['ai.openrouter.provider'].sudo().search(
                [('active', '=', True)], limit=1
            )
            if openrouter_provider and openrouter_provider.embedding_model:
                return openrouter_provider.embedding_model
        return super()._get_embedding_model()
