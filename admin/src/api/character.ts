import { api } from './http';

export interface CharacterInnerDrive {
  id: string;
  name: string;
  desire?: string | null;
  fear?: string | null;
  secret?: string | null;
}

export interface CharacterInnerDriveUpdate {
  desire?: string | null;
  fear?: string | null;
  secret?: string | null;
}

export interface Character {
  id: string;
  name: string;
  description?: string;
  avatar_url?: string;
  desire?: string | null;
  fear?: string | null;
  secret?: string | null;
}

export const characterApi = {
  updateInnerDrive(characterId: string, data: CharacterInnerDriveUpdate): Promise<CharacterInnerDrive> {
    return api.put(`/characters/admin/${characterId}/inner-drive`, data);
  },

  list(): Promise<Character[]> {
    return api.get<{ characters: Character[]; total: number }>('/characters').then(r => r.characters);
  },

  get(characterId: string): Promise<Character> {
    return api.get<Character>(`/characters/${characterId}`);
  },
};
