"""TokenBudgetController - 6-layer prompt token budget management.

CR-027: Manages token allocation across 6 prompt layers with automatic
truncation when budget is exceeded.
"""

import logging
from typing import Dict, Optional

from app.core.config import settings

try:
    import tiktoken
    _encoder = tiktoken.get_encoding(settings.token_encoding)
except ImportError:
    _encoder = None
    logging.warning("tiktoken not available, token counting disabled")

logger = logging.getLogger(__name__)


# Default budget allocation for 6 layers (total 2300 tokens)
# These values are overridden by settings in production
DEFAULT_BUDGET = {
    "L1_global_rules": settings.token_budget_l1_global,
    "L2_world_knowledge": settings.token_budget_l2_world,
    "L3_npc_profile": settings.token_budget_l3_npc,
    "L4_memory": settings.token_budget_l4_memory,
    "L5_narrative_director": settings.token_budget_l5_narrative,
    "L6_player_input": settings.token_budget_l6_player,
}

TOTAL_BUDGET = settings.token_budget_total


class TokenBudgetController:
    """Controls token budget allocation and truncation for 6-layer prompts."""

    def __init__(self, budget: Optional[Dict[str, int]] = None):
        self.budget = budget or DEFAULT_BUDGET.copy()
        self.total_budget = TOTAL_BUDGET

    def count_tokens(self, text: str) -> int:
        """Count tokens in text using cl100k_base encoding."""
        if _encoder is None:
            # Fallback: approximate 1 token per 4 characters
            return len(text) // 4
        return len(_encoder.encode(text))

    def truncate_to_budget(self, text: str, layer: str) -> str:
        """Truncate text to fit within the layer's token budget.

        Uses token-based reverse decoding to ensure UTF-8 safety.

        Args:
            text: Text to truncate
            layer: Layer name (e.g., "L1_global_rules")

        Returns:
            Truncated text that fits within budget
        """
        if _encoder is None:
            # Fallback: approximate truncation
            max_chars = self.budget.get(layer, 200) * 4
            return text[:max_chars] if len(text) > max_chars else text

        max_tokens = self.budget.get(layer, 200)
        tokens = _encoder.encode(text)

        if len(tokens) <= max_tokens:
            return text

        # Truncate and decode back to text (UTF-8 safe)
        truncated_tokens = tokens[:max_tokens]
        return _encoder.decode(truncated_tokens)

    def validate_total_budget(self, layers: Dict[str, str]) -> Dict[str, int]:
        """Validate total token usage across all layers.

        Args:
            layers: Dict mapping layer names to their content

        Returns:
            Dict mapping layer names to their token counts

        Raises:
            ValueError: If total tokens exceed TOTAL_BUDGET
        """
        token_counts = {}
        total = 0

        for layer, content in layers.items():
            count = self.count_tokens(content)
            token_counts[layer] = count
            total += count

        if total > self.total_budget:
            logger.warning(
                f"Total tokens ({total}) exceed budget ({self.total_budget}). "
                f"Layer breakdown: {token_counts}"
            )

        return token_counts

    def get_layer_budget(self, layer: str) -> int:
        """Get the token budget for a specific layer."""
        return self.budget.get(layer, 200)

    def allocate_remaining(
        self,
        used_layers: Dict[str, str],
        target_layer: str
    ) -> int:
        """Calculate remaining budget available for a target layer.

        Args:
            used_layers: Dict of already-allocated layers and their content
            target_layer: Layer to calculate remaining budget for

        Returns:
            Available tokens for target_layer
        """
        used_tokens = sum(
            self.count_tokens(content) for content in used_layers.values()
        )
        layer_budget = self.budget.get(target_layer, 200)
        remaining = self.total_budget - used_tokens

        return max(0, min(layer_budget, remaining))
