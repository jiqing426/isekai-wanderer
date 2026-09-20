"""Unit tests for TokenBudgetController (CR-027)."""

import pytest
from app.services.token_budget import TokenBudgetController


class TestTokenBudgetController:
    """Test token budget control and truncation."""

    def test_count_tokens_basic(self):
        """Test basic token counting."""
        controller = TokenBudgetController()
        
        # Empty text
        assert controller.count_tokens("") == 0
        
        # Simple text
        text = "Hello, world!"
        count = controller.count_tokens(text)
        assert count > 0
        assert isinstance(count, int)

    def test_count_tokens_chinese(self):
        """Test token counting with Chinese text."""
        controller = TokenBudgetController()
        
        # Chinese characters typically use more tokens
        text = "这是一个测试文本"
        count = controller.count_tokens(text)
        assert count > 0

    def test_truncate_to_budget_within_limit(self):
        """Test truncation when text is within budget."""
        controller = TokenBudgetController()
        
        text = "Short text"
        result = controller.truncate_to_budget(text, "L1_global_rules")
        assert result == text

    def test_truncate_to_budget_exceeds_limit(self):
        """Test truncation when text exceeds budget."""
        controller = TokenBudgetController()
        
        # Create text that exceeds L1 budget (200 tokens)
        long_text = "This is a test. " * 100  # ~400 tokens
        result = controller.truncate_to_budget(long_text, "L1_global_rules")
        
        # Result should be shorter
        result_tokens = controller.count_tokens(result)
        assert result_tokens <= 200

    def test_truncate_utf8_safety(self):
        """Test that truncation preserves UTF-8 safety."""
        controller = TokenBudgetController()
        
        # Chinese text with many characters
        long_text = "测试文本" * 100
        result = controller.truncate_to_budget(long_text, "L1_global_rules")
        
        # Should be valid UTF-8
        assert isinstance(result, str)
        # Should not raise encoding errors
        result.encode('utf-8')

    def test_validate_total_budget(self):
        """Test total budget validation."""
        controller = TokenBudgetController()
        
        layers = {
            "L1_global_rules": "Rule 1",
            "L2_world_knowledge": "Knowledge",
            "L3_npc_profile": "Profile",
        }
        
        result = controller.validate_total_budget(layers)
        
        assert "L1_global_rules" in result
        assert "L2_world_knowledge" in result
        assert "L3_npc_profile" in result
        assert all(isinstance(v, int) for v in result.values())

    def test_get_layer_budget(self):
        """Test getting budget for specific layer."""
        controller = TokenBudgetController()
        
        assert controller.get_layer_budget("L1_global_rules") == 200
        assert controller.get_layer_budget("L2_world_knowledge") == 500
        assert controller.get_layer_budget("L3_npc_profile") == 300
        assert controller.get_layer_budget("L4_memory") == 800
        assert controller.get_layer_budget("L5_narrative_director") == 300
        assert controller.get_layer_budget("L6_player_input") == 200

    def test_allocate_remaining(self):
        """Test remaining budget allocation."""
        controller = TokenBudgetController()
        
        # Simulate used layers
        used_layers = {
            "L1_global_rules": "Short rule",
            "L2_world_knowledge": "Some knowledge",
        }
        
        remaining = controller.allocate_remaining(used_layers, "L3_npc_profile")
        
        # Should return positive value
        assert remaining > 0
        assert remaining <= 300  # L3 budget

    def test_allocate_remaining_exhausted(self):
        """Test allocation when budget is exhausted."""
        controller = TokenBudgetController()
        
        # Use up most of the budget
        used_layers = {
            "L1_global_rules": "x" * 800,
            "L2_world_knowledge": "y" * 2000,
            "L3_npc_profile": "z" * 1200,
        }
        
        remaining = controller.allocate_remaining(used_layers, "L4_memory")
        
        # Should return 0 or small value
        assert remaining >= 0

    def test_custom_budget(self):
        """Test controller with custom budget."""
        custom_budget = {
            "L1_global_rules": 100,
            "L2_world_knowledge": 200,
            "L3_npc_profile": 150,
            "L4_memory": 400,
            "L5_narrative_director": 150,
            "L6_player_input": 100,
        }
        
        controller = TokenBudgetController(budget=custom_budget)
        
        assert controller.get_layer_budget("L1_global_rules") == 100
        assert controller.get_layer_budget("L4_memory") == 400
