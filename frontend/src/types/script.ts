/**
 * 剧本详情相关类型定义 (CR-013)
 */

export interface ScriptDetail {
  scriptId: string;
  title: string;
  cover: string;
  description: string;
  author: string;
  chapters: Chapter[];
  totalNodes: number;
  unlockedNodes: number;
  completionRate: number;
}

export interface Chapter {
  chapterId: string;
  title: string;
  nodes: ScriptNode[];
}

export interface ScriptNode {
  nodeId: string;
  type: 'fixed_scene' | 'ai_dialog' | 'choice_point' | 'converge_node' | 'cg_trigger' | 'ending_node';
  title: string;
  content?: string;
  isUnlocked: boolean;
  // 类型特定字段
  background?: string;
  characterId?: string;
  characterName?: string;
  dialogueOptions?: string[];
  choices?: Choice[];
  description?: string;
  cgId?: string;
  cgUrl?: string;
  endingType?: 'good' | 'normal' | 'bad';
}

export interface Choice {
  text: string;
  nextNodeId: string;
}
