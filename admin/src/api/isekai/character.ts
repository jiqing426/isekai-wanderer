import { defHttp } from '@/utils/http/axios';

// Note: The isekai backend returns raw JSON (not wrapped in {code, result, message}),
// so we use isTransformResponse: false to bypass Vben's response transformer.

export interface Character {
  id: string;
  name: string;
  description?: string;
  avatar_url?: string;
  desire?: string | null;
  fear?: string | null;
  secret?: string | null;
}

export interface CharacterInnerDriveUpdate {
  desire?: string | null;
  fear?: string | null;
  secret?: string | null;
}

export const characterApi = {
  list(): Promise<Character[]> {
    return defHttp.get<{ characters: Character[]; total: number }>(
      { url: '/characters' },
      { isTransformResponse: false },
    ).then((r) => r.characters);
  },

  get(characterId: string): Promise<Character> {
    return defHttp.get<Character>(
      { url: `/characters/${characterId}` },
      { isTransformResponse: false },
    );
  },

  updateInnerDrive(characterId: string, data: CharacterInnerDriveUpdate): Promise<Character> {
    return defHttp.put<Character>(
      { url: `/characters/admin/${characterId}/inner-drive`, params: data },
      { isTransformResponse: false },
    );
  },
};
