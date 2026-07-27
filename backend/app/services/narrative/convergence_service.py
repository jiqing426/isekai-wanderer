"""ConvergenceService — DEV-BE-004 (v4.4 dual-agent architecture).

Manages convergence points where multiple character routes merge.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.convergence_point import ConvergencePoint
from app.models.game import GameSession


class ConvergenceService:
    """Service for checking and generating convergence point scenes."""

    async def check_convergence(
        self,
        db: AsyncSession,
        session_id: str,
        user_id: str,
        character_id: str,
    ) -> Optional[ConvergencePoint]:
        """
        Check if the current game session has reached a convergence point.
        
        Returns the convergence point if reached, None otherwise.
        """
        # Get game session
        session_uuid = UUID(session_id) if isinstance(session_id, str) else session_id
        result = await db.execute(select(GameSession).where(GameSession.id == session_uuid))
        session = result.scalar_one_or_none()
        
        if not session:
            return None
        
        script_id = session.script_id
        
        # Get all convergence points for this script
        stmt = select(ConvergencePoint).where(
            ConvergencePoint.script_id == script_id
        ).order_by(ConvergencePoint.chapter)
        result = await db.execute(stmt)
        convergence_points = result.scalars().all()
        
        if not convergence_points:
            return None
        
        # Count rounds played in current segment
        rounds_played = await self._count_rounds_in_segment(db, session_id)
        
        # Check if any convergence point is reached
        for cp in convergence_points:
            required = cp.required_rounds.get(character_id, 4)
            if rounds_played >= required:
                return cp
        
        return None

    async def _count_rounds_in_segment(self, db: AsyncSession, session_id: str) -> int:
        """
        Count the number of rounds played in the current segment.
        
        A "round" is one dialogue + choice cycle.
        """
        # TODO: Query game_progress or dialogue_history to count actual rounds
        # For now, return 0 as placeholder
        return 0

    async def generate_convergence_scene(
        self,
        convergence_point: ConvergencePoint,
        user_id: str,
        character_id: str,
        affection_value: int,
    ) -> dict:
        """
        Generate the scene for a convergence point.
        
        Returns a dict with narrative text and choices.
        """
        # If preset content exists, use it
        if convergence_point.content.get("preset"):
            return convergence_point.content
        
        # Otherwise, call LLM to generate
        from app.llm.model_router import model_router, ScenarioType
        import json
        
        prompt = f"""请生成集合点「{convergence_point.title}」的剧情。

## 集合点描述
{convergence_point.description}

## 当前角色
角色ID: {character_id}
当前好感度: {affection_value}%

## 要求
1. 这是所有角色路线汇聚的关键节点
2. 生成200-400字的叙事文本
3. 生成2-3个新的分支选项（基于累积好感度和角色性格）
4. 每个选项标注好感度影响（±5以内）

输出JSON格式：
{{
  "narrative": "叙事文本",
  "choices": [
    {{"text": "选项文本", "hint": "角色可能的反应", "affection_delta": 5}},
    ...
  ]
}}"""
        
        try:
            import asyncio
            # 添加 10 秒超时控制
            response = await asyncio.wait_for(
                model_router.call_with_fallback(
                    scenario=ScenarioType.CONVERGENCE,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                ),
                timeout=10.0
            )
            
            return json.loads(response.get("text", "{}"))
        except asyncio.TimeoutError:
            # LLM 超时，返回默认场景
            return {
                "narrative": convergence_point.description,
                "choices": [
                    {"text": "继续前进", "hint": "", "affection_delta": 0},
                ],
            }
        except Exception as e:
            # Fallback if LLM fails
            return {
                "narrative": convergence_point.description,
                "choices": [
                    {"text": "继续前进", "hint": "", "affection_delta": 0},
                ],
            }


# Global singleton
convergence_service = ConvergenceService()
