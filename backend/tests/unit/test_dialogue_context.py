"""Unit tests for DialogueContextManager (Phase 3, Task 2)."""

import pytest
from app.services.dialogue.context_manager import DialogueContextManager, DialogueMessage


class TestDialogueContextManager:
    """Tests for DialogueContextManager class."""

    def test_init_default(self):
        """Test default initialization."""
        mgr = DialogueContextManager()
        assert mgr.max_tokens == 2048
        assert mgr.reserve_tokens == 300
        assert mgr.effective_tokens == 1748
        assert mgr.messages == []
        assert mgr.current_emotion is None

    def test_init_custom(self):
        """Test custom initialization."""
        mgr = DialogueContextManager(max_tokens=4096, model="gpt-3.5-turbo", reserve_tokens=500)
        assert mgr.max_tokens == 4096
        assert mgr.reserve_tokens == 500
        assert mgr.effective_tokens == 3596

    def test_add_message(self):
        """Test adding messages to history."""
        mgr = DialogueContextManager()
        mgr.add_message("user", "Hello")
        mgr.add_message("assistant", "Hi there!")
        assert len(mgr.messages) == 2
        assert mgr.messages[0].role == "user"
        assert mgr.messages[0].content == "Hello"
        assert mgr.messages[1].role == "assistant"

    def test_add_message_with_emotion(self):
        """Test adding message with emotion."""
        mgr = DialogueContextManager()
        mgr.add_message("assistant", "I'm happy!", emotion="happy")
        assert mgr.current_emotion == "happy"
        assert mgr.messages[0].emotion == "happy"

    def test_set_emotion(self):
        """Test setting emotion state."""
        mgr = DialogueContextManager()
        mgr.set_emotion("sad")
        assert mgr.current_emotion == "sad"

    def test_get_context_empty(self):
        """Test get_context with empty history."""
        mgr = DialogueContextManager()
        ctx = mgr.get_context()
        assert ctx == []

    def test_get_context_basic(self):
        """Test get_context with basic messages."""
        mgr = DialogueContextManager()
        mgr.add_message("user", "Hello")
        mgr.add_message("assistant", "Hi!")
        ctx = mgr.get_context(inject_memories=False)
        assert len(ctx) == 2
        assert ctx[0]["role"] == "user"
        assert ctx[1]["role"] == "assistant"

    def test_get_context_with_memories(self):
        """Test get_context with memory injection."""
        mgr = DialogueContextManager()
        mgr.add_message("user", "Hello")
        memories = ["User likes apples", "User is brave"]
        ctx = mgr.get_context(memories=memories, inject_memories=True)
        # Should have memory system message + user message
        assert len(ctx) == 2
        assert ctx[0]["role"] == "system"
        assert "Character Memories" in ctx[0]["content"]
        assert "apples" in ctx[0]["content"]
        assert ctx[1]["role"] == "user"

    def test_get_context_without_memory_injection(self):
        """Test get_context with inject_memories=False."""
        mgr = DialogueContextManager()
        mgr.add_message("user", "Hello")
        memories = ["User likes apples"]
        ctx = mgr.get_context(memories=memories, inject_memories=False)
        assert len(ctx) == 1
        assert ctx[0]["role"] == "user"

    def test_token_trimming_under_budget(self):
        """Test that messages under budget are not trimmed."""
        mgr = DialogueContextManager(max_tokens=10000)
        for i in range(5):
            mgr.add_message("user", f"Short message {i}")
        ctx = mgr.get_context(inject_memories=False)
        assert len(ctx) == 5

    def test_token_trimming_over_budget(self):
        """Test that messages over budget are trimmed."""
        mgr = DialogueContextManager(max_tokens=100, reserve_tokens=20)
        # Add many messages to exceed budget
        for i in range(50):
            mgr.add_message("user", f"This is message number {i} with some content to use tokens")
        ctx = mgr.get_context(inject_memories=False)
        # Should be trimmed to fit within 80 effective tokens
        assert len(ctx) < 50
        # Should keep recent messages (higher indices)
        assert any("49" in m["content"] for m in ctx)

    def test_token_trimming_preserves_system(self):
        """Test that system messages are preserved during trimming."""
        mgr = DialogueContextManager(max_tokens=100, reserve_tokens=20)
        mgr.add_message("system", "You are a helpful assistant with specific personality traits")
        for i in range(50):
            mgr.add_message("user", f"This is user message number {i}")
        ctx = mgr.get_context(inject_memories=False)
        # System message should be first
        assert ctx[0]["role"] == "system"
        assert "helpful assistant" in ctx[0]["content"]

    def test_token_trimming_keeps_recent(self):
        """Test that recent messages are kept during trimming."""
        mgr = DialogueContextManager(max_tokens=80, reserve_tokens=10)
        for i in range(20):
            mgr.add_message("user", f"Message {i} content here")
        ctx = mgr.get_context(inject_memories=False)
        # Should have recent messages (19, 18, etc.) not old (0, 1)
        content_str = " ".join(m["content"] for m in ctx)
        assert "19" in content_str or "18" in content_str
        assert "Message 0" not in content_str

    def test_get_context_with_style_no_emotion(self):
        """Test get_context_with_style without emotion."""
        mgr = DialogueContextManager()
        mgr.add_message("user", "Hello")
        ctx = mgr.get_context_with_style(base_style="Formal and polite")
        assert len(ctx) >= 1
        # First should be style system prompt
        if ctx[0]["role"] == "system":
            assert "Formal and polite" in ctx[0]["content"]

    def test_get_context_with_style_and_emotion(self):
        """Test get_context_with_style with emotion."""
        mgr = DialogueContextManager()
        mgr.add_message("user", "Hello")
        mgr.set_emotion("happy")
        ctx = mgr.get_context_with_style(base_style="Neutral character")
        system_msgs = [m for m in ctx if m["role"] == "system"]
        assert len(system_msgs) >= 1
        assert "happy" in system_msgs[0]["content"].lower() or "warmth" in system_msgs[0]["content"].lower()

    def test_emotion_style_mapping(self):
        """Test emotion to style mapping."""
        mgr = DialogueContextManager()
        emotions_and_keywords = {
            "happy": ["warmth", "enthusiasm"],
            "sad": ["melancholy", "softer"],
            "angry": ["intensity", "forceful"],
            "fearful": ["caution", "hesitant"],
            "surprised": ["wonder", "exclamatory"],
            "neutral": ["calm", "balanced"],
        }
        for emotion, keywords in emotions_and_keywords.items():
            mgr.clear()
            mgr.set_emotion(emotion)
            mgr.add_message("user", "Hello")
            ctx = mgr.get_context_with_style()
            system_msgs = [m for m in ctx if m["role"] == "system"]
            if system_msgs:
                content = system_msgs[0]["content"].lower()
                assert any(kw in content for kw in keywords), f"Emotion '{emotion}' missing keywords"

    def test_clear(self):
        """Test clearing dialogue history."""
        mgr = DialogueContextManager()
        mgr.add_message("user", "Hello")
        mgr.add_message("assistant", "Hi!")
        mgr.set_emotion("happy")
        mgr.injected_memories = ["memory1"]
        assert len(mgr) == 2

        mgr.clear()
        assert len(mgr) == 0
        assert mgr.current_emotion is None
        assert mgr.injected_memories == []

    def test_get_stats(self):
        """Test get_stats returns correct information."""
        mgr = DialogueContextManager(max_tokens=2048)
        mgr.add_message("user", "Hello world")
        mgr.add_message("assistant", "Hi there!")
        mgr.set_emotion("happy")
        mgr.injected_memories = ["mem1", "mem2"]

        stats = mgr.get_stats()
        assert stats["message_count"] == 2
        assert stats["max_tokens"] == 2048
        assert stats["effective_tokens"] == 1748
        assert stats["current_emotion"] == "happy"
        assert stats["injected_memories"] == 2
        assert stats["total_tokens"] > 0

    def test_len(self):
        """Test __len__ returns message count."""
        mgr = DialogueContextManager()
        assert len(mgr) == 0
        mgr.add_message("user", "Hello")
        assert len(mgr) == 1
        mgr.add_message("assistant", "Hi")
        assert len(mgr) == 2

    def test_repr(self):
        """Test __repr__ returns string representation."""
        mgr = DialogueContextManager()
        mgr.add_message("user", "Hello")
        mgr.set_emotion("happy")
        repr_str = repr(mgr)
        assert "DialogueContextManager" in repr_str
        assert "messages=1" in repr_str
        assert "happy" in repr_str

    def test_memory_formatting(self):
        """Test memory formatting in context."""
        mgr = DialogueContextManager()
        mgr.add_message("user", "Hello")
        memories = [
            "User defeated the dragon",
            "User's name is Alex",
            "User helped the village",
        ]
        ctx = mgr.get_context(memories=memories)
        memory_msg = ctx[0]
        assert "1." in memory_msg["content"]
        assert "2." in memory_msg["content"]
        assert "3." in memory_msg["content"]
        assert "dragon" in memory_msg["content"]

    def test_count_tokens_with_encoding(self):
        """Test token counting with tiktoken."""
        mgr = DialogueContextManager()
        tokens = mgr._count_tokens("Hello world")
        assert tokens > 0
        assert tokens < 10  # "Hello world" is ~2 tokens

    def test_count_tokens_empty(self):
        """Test token counting with empty string."""
        mgr = DialogueContextManager()
        assert mgr._count_tokens("") == 0

    def test_count_tokens_fallback(self):
        """Test token counting fallback without encoding."""
        mgr = DialogueContextManager()
        mgr.encoding = None  # Force fallback
        tokens = mgr._count_tokens("Hello world, this is a test")
        # Fallback: ~4 chars per token → ~7 tokens
        assert tokens > 0

    def test_message_metadata(self):
        """Test message metadata storage."""
        mgr = DialogueContextManager()
        mgr.add_message("user", "Hello", metadata={"source": "chat"})
        assert mgr.messages[0].metadata == {"source": "chat"}

    def test_message_timestamp(self):
        """Test message auto-timestamp."""
        mgr = DialogueContextManager()
        mgr.add_message("user", "Hello")
        assert mgr.messages[0].timestamp is not None

    def test_injected_memories_tracking(self):
        """Test that injected memories are tracked."""
        mgr = DialogueContextManager()
        mgr.add_message("user", "Hello")
        memories = ["mem1", "mem2"]
        mgr.get_context(memories=memories, inject_memories=True)
        assert mgr.injected_memories == memories

    def test_get_context_with_style_and_memories(self):
        """Test combined style + memories in context."""
        mgr = DialogueContextManager()
        mgr.add_message("user", "Hello")
        mgr.set_emotion("happy")
        ctx = mgr.get_context_with_style(
            memories=["User is brave"],
            base_style="Heroic character"
        )
        # Should have style system + memory system + user message
        system_count = sum(1 for m in ctx if m["role"] == "system")
        assert system_count >= 1

    def test_trimming_with_very_long_message(self):
        """Test trimming with a very long single message."""
        mgr = DialogueContextManager(max_tokens=50, reserve_tokens=10)
        long_text = "word " * 200  # ~200 tokens
        mgr.add_message("user", long_text)
        mgr.add_message("assistant", "Short reply")
        ctx = mgr.get_context(inject_memories=False)
        # At minimum the assistant message should survive (it's shorter)
        assert len(ctx) >= 1

    def test_emotion_persistence(self):
        """Test emotion persists across messages."""
        mgr = DialogueContextManager()
        mgr.add_message("assistant", "Happy!", emotion="happy")
        mgr.add_message("user", "Question")
        # Current emotion should still be happy
        assert mgr.current_emotion == "happy"
        # But user message without explicit emotion should inherit
        assert mgr.messages[1].emotion == "happy"
