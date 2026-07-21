import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class AIEmbedding(models.Model):
    _inherit = 'ai.embedding'

    def _get_openrouter_provider_for_embedding(self, embedding_model):
        openrouter_provider = self.env["ai.openrouter.provider"].sudo().search(
            [("active", "=", True), ("embedding_model_id.external_id", "=", embedding_model)], limit=1
        )
        if openrouter_provider:
            return "openrouter"

    @api.model
    def _cron_generate_embedding(self, batch_size=100):
        try:
            from odoo.addons.ai.utils import llm_providers
            import odoo.addons.ai.models.ai_embedding as embedding_module

            _original_fn = getattr(llm_providers, 'get_provider_for_embedding_model', None)
            _original_local = getattr(embedding_module, 'get_provider_for_embedding_model', None)

            def _patched_get_provider_for_embedding_model(env, embedding_model):
                result = self._get_openrouter_provider_for_embedding(embedding_model)
                if result:
                    return result
                if _original_fn:
                    return _original_fn(env, embedding_model)
                raise UserError("No provider found for embedding model")

            llm_providers.get_provider_for_embedding_model = _patched_get_provider_for_embedding_model
            embedding_module.get_provider_for_embedding_model = _patched_get_provider_for_embedding_model
        except ImportError:
            _logger.warning("OpenRouter: could not patch embedding provider lookup")

        return super()._cron_generate_embedding(batch_size=batch_size)
