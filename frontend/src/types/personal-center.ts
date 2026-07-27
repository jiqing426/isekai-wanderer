/**
 * Personal Center types from API Contract (CR-008)
 */

export interface UserStats {
  scripts_completed: number;
  total_play_time_minutes: number;
  endings_unlocked: number;
  cgs_collected: number;
  total_dialogues: number;
  total_choices: number;
}

export interface UserAsset {
  balance: number;
  total_earned: number;
  total_spent: number;
}

export interface SignInfo {
  checked_in_today: boolean;
  streak_days: number;
  total_checkins: number;
  total_fragments: number;
  this_week: boolean[];
  next_milestone: {
    days: number;
    reward_type: string;
    reward_amount: number;
  } | null;
}

export interface LatestSave {
  id: string;
  session_id: string;
  script_id: string;
  script_name: string;
  character_name: string;
  character_avatar: string;
  current_node_id: string;
  label: string;
  choice_count: number;
  created_at: string;
  updated_at: string;
}

export interface MemorySummary {
  total_memories: number;
  recent: Array<{
    id: string;
    character_id: string;
    character_name: string;
    content: string;
    created_at: string;
  }>;
  preferences?: Array<{
    id: string;
    description: string;
    created_at: string;
  }>;
  bonds?: Array<{
    id: string;
    character_name: string;
    description: string;
    created_at: string;
  }>;
  events?: Array<{
    id: string;
    description: string;
    created_at: string;
  }>;
  is_full_available: boolean;
}

export interface CharacterBond {
  id: string;
  name: string;
  avatar_url: string;
  affection_value: number;
  affection_level: string;
  max_affection: number;
}

export interface BondList {
  characters: CharacterBond[];
  total: number;
}

export interface EndingProgress {
  script_id: string;
  script_name: string;
  total_endings: number;
  unlocked_endings: number;
  ending_types: string[];
  completion_rate: number;
}

export interface EndingsList {
  endings: EndingProgress[];
  total_scripts: number;
  total_endings_unlocked: number;
}

export interface RecentEnding {
  id: string;
  script_name: string;
  character_name: string;
  ending_type: 'good' | 'normal' | 'bad' | 'true';
  ending_title: string;
  ended_at: string;
}

export interface RecentEndings {
  recent_endings: RecentEnding[];
  total: number;
}

export interface FullMemory {
  id: string;
  character_id: string;
  character_name: string;
  content: string;
  source: string;
  created_at: string;
}

export interface FullMemoryList {
  memories: FullMemory[];
  total: number;
}
