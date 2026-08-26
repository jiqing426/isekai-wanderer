"""PromptBuilder - 6-layer structured prompt construction system.

CR-027: Builds prompts from 6 layers with graceful degradation:
- L1: Global rules (system prompt base)
- L2: World knowledge (Lorebook entries matched by scene tags)
- L3: NPC profile (character info + desire/fear/secret)
- L3.5: Player Identity (CR-028: player's chosen character role)
- L4: Memory (recalled memories)
- L5: Narrative director (story context, rules)
- L6: Player input (current user input)
"""

import logging
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.token_budget import TokenBudgetController
from app.services.lorebook_service import LorebookService
from app.services.scene_config_service import SceneConfigService
from app.services.narrative.memory_service import MemoryService
from app.models.script import Character

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds 6-layer structured prompts with token budget management."""

    def __init__(
        self,
        db: AsyncSession,
        lorebook_service: Optional[LorebookService] = None,
        scene_config_service: Optional[SceneConfigService] = None,
        memory_service: Optional[MemoryService] = None,
        budget_controller: Optional[TokenBudgetController] = None,
    ):
        self.db = db
        self.lorebook_service = lorebook_service or LorebookService(db)
        self.scene_config_service = scene_config_service or SceneConfigService(db)
        self.memory_service = memory_service or MemoryService(db)
        self.budget = budget_controller or TokenBudgetController()

    async def build_prompt(
        self,
        user_id: UUID,
        character: Character,
        node_id: UUID,
        user_input: str,
        story_context: str = "",
        affection_level: int = 0,
        player_character: Optional[Character] = None,  # CR-028: player's chosen role
    ) -> Dict[str, str]:
        """Build complete 6-layer prompt.

        Args:
            user_id: Current user ID
            character: Character model instance
            node_id: Current story node ID
            user_input: Player's current input
            story_context: Additional story context
            affection_level: Current affection level with character

        Returns:
            Dict with 'system_prompt' and 'user_prompt' keys
        """
        layers: Dict[str, str] = {}

        # L1: Global rules
        layers["L1_global_rules"] = self._build_global_rules()

        # L2: World knowledge (from Lorebook + SceneConfig)
        layers["L2_world_knowledge"] = await self._build_world_knowledge(node_id)

        # L3: NPC profile
        layers["L3_npc_profile"] = self._build_npc_profile(character, affection_level)

        # L3.5: Player Identity (CR-028: player's chosen character role)
        if player_character:
            layers["L3.5_player_identity"] = self._build_player_identity(player_character)

        # L4: Memory
        layers["L4_memory"] = await self._build_memory(user_id, character.id, user_input)

        # L5: Narrative director
        layers["L5_narrative_director"] = self._build_narrative_director(story_context)

        # L6: Player input
        layers["L6_player_input"] = user_input

        # Apply token budget truncation
        truncated_layers = {}
        for layer_name, content in layers.items():
            truncated_layers[layer_name] = self.budget.truncate_to_budget(content, layer_name)

        # Validate total budget
        token_counts = self.budget.validate_total_budget(truncated_layers)
        logger.debug(f"Prompt token distribution: {token_counts}")

        # Assemble final prompts
        system_prompt = self._assemble_system_prompt(truncated_layers)
        user_prompt = truncated_layers["L6_player_input"]

        return {
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "token_counts": token_counts,
        }

    def _build_global_rules(self) -> str:
        """L1: Build global rules layer."""
        return """You are a narrative AI in an interactive story game. Your role is to:
1. Stay in character and maintain consistency
2. Respond naturally to player input
3. Advance the story based on context
4. Respect the world's lore and rules
5. Keep responses engaging and immersive

Always respond in the language the player uses. Be creative but consistent with established facts."""

    async def _build_world_knowledge(self, node_id: UUID) -> str:
        """L2: Build world knowledge layer from Lorebook and SceneConfig.

        Graceful degradation: returns empty string on failure.
        """
        try:
            # Get scene config for current node
            scene_config = await self.scene_config_service.get_by_node_id(node_id)

            if not scene_config:
                return ""

            # Match lorebook entries by scene tags
            scene_tags = scene_config.get("tags", [])
            if not scene_tags:
                return scene_config.get("description", "")

            # Query lorebook entries matching these tags
            entries = await self.lorebook_service.match_by_tags(
                tags=scene_tags,
                limit=10
            )

            # Build world knowledge text
            knowledge_parts = []

            # Add scene description
            if scene_config.get("description"):
                knowledge_parts.append(f"[Current Scene] {scene_config['description']}")

            # Add matched lorebook entries
            for entry in entries:
                knowledge_parts.append(f"[{entry['title']}] {entry['content']}")

            return "\n\n".join(knowledge_parts)

        except Exception as e:
            logger.warning(f"L2 world knowledge build failed: {e}")
            return ""

    def _build_npc_profile(self, character: Character, affection_level: int) -> str:
        """L3: Build NPC profile layer with inner drive.

        Graceful degradation: handles missing desire/fear/secret fields.
        """
        parts = [f"[Character: {character.name}]"]

        if character.description:
            parts.append(f"Personality: {character.description}")

        # CR-027: Add inner drive (desire/fear/secret)
        # Graceful degradation: fields may be None
        desire = getattr(character, "desire", None)
        fear = getattr(character, "fear", None)
        secret = getattr(character, "secret", None)

        if desire:
            parts.append(f"Inner Desire: {desire}")
        if fear:
            parts.append(f"Deep Fear: {fear}")
        if secret:
            parts.append(f"Hidden Secret: {secret} (never reveal directly)")

        # Add affection context
        if affection_level > 80:
            parts.append("Relationship: Very close, deep trust")
        elif affection_level > 50:
            parts.append("Relationship: Good friends")
        elif affection_level > 20:
            parts.append("Relationship: Acquaintances")
        else:
            parts.append("Relationship: Strangers, cautious")

        return "\n".join(parts)

    async def _build_memory(
        self,
        user_id: UUID,
        character_id: UUID,
        query_text: str
    ) -> str:
        """L4: Build memory layer from recalled memories.

        Graceful degradation: returns empty string on failure.
        """
        try:
            memories = await self.memory_service.recall(
                user_id=user_id,
                character_id=character_id,
                query_text=query_text,
                limit=5
            )

            if not memories:
                return ""

            memory_lines = [f"- {m.get('memory_text', '')}" for m in memories]
            return "[Relevant Memories]\n" + "\n".join(memory_lines)

        except Exception as e:
            logger.warning(f"L4 memory build failed: {e}")
            return ""

    def _build_narrative_director(self, story_context: str) -> str:
        """L5: Build narrative director layer."""
        if not story_context:
            return "[Story Context] Continue the current narrative naturally."

        return f"[Story Context]\n{story_context}"

    def _build_player_identity(self, player_character: Character) -> str:
        """L3.5: Build player identity layer (CR-028).
        
        Injects the player's chosen character role into the prompt.
        This allows NPCs to react to the player's role-playing choice.
        
        Args:
            player_character: The character the player chose to play as
            
        Returns:
            Player identity description string
        """
        parts = [f"[Player Role: {player_character.name}]"]
        
        if player_character.description:
            parts.append(f"Background: {player_character.description}")
        
        if player_character.play_description:
            parts.append(f"Role Context: {player_character.play_description}")
        
        # Add personality traits if available
        if player_character.personality:
            traits = []
            for trait, value in player_character.personality.items():
                if value > 0:
                    traits.append(f"{trait}({value})")
            if traits:
                parts.append(f"Personality: {', '.join(traits)}")
        
        return "\n".join(parts)

    def _assemble_system_prompt(self, layers: Dict[str, str]) -> str:
        """Assemble system prompt from L1-L5 layers."""
        parts = []

        # L1: Global rules
        if layers.get("L1_global_rules"):
            parts.append(layers["L1_global_rules"])

        # L2: World knowledge
        if layers.get("L2_world_knowledge"):
            parts.append("\n[World Knowledge]")
            parts.append(layers["L2_world_knowledge"])

        # L3: NPC profile
        if layers.get("L3_npc_profile"):
            parts.append("\n[Character Profile]")
            parts.append(layers["L3_npc_profile"])

        # L3.5: Player identity (CR-028)
        if layers.get("L3.5_player_identity"):
            parts.append("\n[Player Identity]")
            parts.append(layers["L3.5_player_identity"])

        # L4: Memory
        if layers.get("L4_memory"):
            parts.append("\n")
            parts.append(layers["L4_memory"])

        # L5: Narrative director
        if layers.get("L5_narrative_director"):
            parts.append("\n")
            parts.append(layers["L5_narrative_director"])

        return "\n".join(parts)
